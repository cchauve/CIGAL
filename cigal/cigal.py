#!/usr/bin/python
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

""" Compute gene clusters of 2 fasta sequesences of gene identifiers
in FASTA format using the connecting intervals algorithm described in

  Quadratic Time Algorithms for Finding Common Intervals in Two and More
  Sequences
  T. Schmidt, J. Stoye. Proceedings of CPM 2004, LNCS 3109, 347-359, 2004.
"""

# TODO: find a better name (Scoipr ?) (Ciggal ?)

import sys
from sets import Set
from pprint import pprint
from cPickle import dump
from config import NAME, VERSION, CLI

class KeyMapper:
    """Like a dict but the mapping to uniq numeric key is automatic."""
    def __init__(self):
        self.cur_key = 0 # first key will be 1
        self.map = {}

    def __getitem__(self, item):
        val = self.map.get(item)
        if not val:
            self.cur_key += 1
            val = self.map[item] = self.cur_key
        return val

    def values(self):
        return self.map.values()

    def items(self):
        return self.map.items()

    def keys(self):
        return self.map.keys()

    def revmap(self):
	return dict(zip(self.map.values(), self.map.keys()))


def parse_fasta(filename, mapper):
    """Parse a FASTA file into a list of integers,
    mapper should be a dict or a KeyMapper."""
    lines = map(lambda l:l.strip(),
                open(filename).readlines())
    lines = filter(lambda l:l,
                   lines)

    name = lines[0][0] == ">" and lines[0][1:] or "unknown"
    
    lines = filter(lambda l:l[0] != ">",
                   lines)
    
    identifiers = filter(lambda x:x,
			 " ".join(lines).split(" "))
    signs = map(lambda x:not x[0]=="-", identifiers)
    identifiers = map(lambda x:x.strip().lstrip("+-"),
		      identifiers)
    
    return map(lambda i:mapper[i], identifiers), signs, name


def pre_process(seq):
    """compute the pos dict (a vector in the paper) and the num matrix
    (paper p.4)"""
    pos = {}
    for i, c in enumerate(seq):
        pos[c] = pos.get(c, []) + [i]
        
    num = []
    for i in range(len(seq)):
        row = []
        for j in range(len(seq)):
            if j < i:
                row.append(0)
            else:
                subseq = seq[i:j+1]
                alpha_size = len(dict(zip(subseq, subseq)).keys())
                row.append(alpha_size)
        num.append(row)
    return pos, num


def left_maximal_p(seq, i, j):
    return i == 0 or seq[i - 1] != seq[j]


def right_maximal_p(seq, i, j, occ):
    return j+1 == len(seq) or seq[j+1] not in occ


def remove_dups(lst):
    seen = {}
    def new_p(elt):
        val = seen.get(elt, True)
        seen[elt] = False
        return val
    return filter(lambda x:new_p(x), lst)


def compute_ci(s1, s2, pos, num):
    """algorithm 1 (paper p.5)"""

    intervals = []
    
    for i in range(len(s2)):
	occ = Set()
	j = i
        v = [False for k in range(len(s1))]
        while j < len(s2) and left_maximal_p(s2, i, j):
            c = s2[j]
	    occ.add(c)
            
	    while not right_maximal_p(s2, i, j, occ):
                j += 1

            for p in pos.get(c, []):
                v[p] = True

            for p in pos.get(c, []):
                p_ = p
                while p_ and v[p_-1]:
                    p_ -= 1
                while p+1 < len(s1) and v[p+1]:
                    p += 1
                start, stop = p_, p
                if num[start][stop] == len(occ):
                    intervals.append(((i+1, j+1), (p_+1, p+1)))
            j += 1
    return remove_dups(intervals)


def draw_ci(mapper, s1, s2, ci):
    # import here so there is no dep on PIL
    from PIL import Image, ImageDraw, ImageFont

    pad = 5
    w, h = len(s1)+1, len(s2)+1
    font = ImageFont.load_default()
    l_sizes = map(lambda l:font.getsize(l), mapper.keys())
    t_w = max(map(lambda s:s[0], l_sizes)) + pad
    t_h = max(map(lambda s:s[1], l_sizes)) + pad
    l_h = l_w = max([t_w, t_h])
    revmap = mapper.revmap()
    img = Image.new("RGB", (w*l_w, h*l_h))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, w*l_w, h*l_h], fill="#000000")

    # grid
    for i in range(w):
	draw.line([(i+1)*l_w, 0, (i+1)*l_w, h*l_h], fill="#3b3b3b")
    for i in range(h):
	draw.line([0, (i+1)*l_h, w*l_w, (i+1)*l_h], fill="#3b3b3b")

    # add labels
    for i, c in enumerate(s1):
	draw.text(((i+1)*l_w+pad/2, 0), revmap[c], font=font, fill="#ffffff")
    for i, c in enumerate(s2):
	draw.text((pad/2, (i+1)*l_h), revmap[c], font=font, fill="#ffffff")

    # draw the rectangles
    for p1, p2 in ci:
	# PIL can't change the pen weight so we do it by hand...
	draw.rectangle([(p1[0]+1)*l_w,
			(p2[0]+1)*l_h,
			(p1[1]+1)*l_w,
			(p2[1]+1)*l_h],
		       outline="#ffffff")	
	draw.rectangle([(p1[0]+1)*l_w-1,
			(p2[0]+1)*l_h-1,
			(p1[1]+1)*l_w+1,
			(p2[1]+1)*l_h+1],
		       outline="#ffffff")	
	draw.rectangle([(p1[0]+1)*l_w+1,
			(p2[0]+1)*l_h+1,
			(p1[1]+1)*l_w-1,
			(p2[1]+1)*l_h-1],
		       outline="#ffffff")	
    img.save("/tmp/foo2.png")


def ci_from_fasta(f1, f2, outfile):
    mapper = KeyMapper()
    s1, s1_signs, s1_name = parse_fasta(f1, mapper)
    s2, s2_signs, s2_name = parse_fasta(f2, mapper)

    pos, num = pre_process(s1)

    ci = compute_ci(s1, s2, pos, num)

    f = open(outfile, "w")
    dump([mapper.revmap(),
	  s1, s1_signs, s1_name,
	  s2, s2_signs, s2_name,
	  ci], f, -1)
    f.close()


def main():
    if len(sys.argv) != 4:
        print NAME, VERSION, "\n"
        print "USAGE: %s SEQ1 SEQ2 OUT" % CLI
        print "  where SEQ1 and SEQ2 are filenames of FASTA",
        print "formated gene sequences"
	print "  and OUT is the output file"
	print "  leading '+' and '-' are discarded from idenfifiers "
        sys.exit(1)
    else:
        ci_from_fasta(sys.argv[1], sys.argv[2], sys.argv[3])    
    
if __name__ == "__main__":
    main()
