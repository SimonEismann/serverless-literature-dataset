#!/usr/bin/env python3

import json
import random
import os
import glob

prefix = "serverless"
basefiles = glob.glob("*-literature-base.json")
if len(basefiles) == 1:
	prefix = os.path.basename(basefiles[0]).split("-")[0]

base_filename = "{}-literature-base.json".format(prefix)
analysis_filename = "{}-literature-analysis.json".format(prefix)
biblio_filename = "{}-literature-bibliography.json".format(prefix)
tech_filename = "{}-literature-technologies.json".format(prefix)

f = open(base_filename)
base = json.load(f)

f = open(biblio_filename)
biblio = json.load(f)

f = open(analysis_filename)
analysis = json.load(f)

f = open(tech_filename)
tech = json.load(f)

debug = False

authorworks = {}
for ident in sorted(biblio):
	authors = biblio[ident]["author"].replace("\xa0", " ")
	cc = authors.count(",")
	ac = authors.count("and ")
	noswap = False
	nosplit = False
	anom = False
	if not (cc == ac + 1 and ac > 0) and not cc == ac:
		anom = True
		if ac == 0:
			noswap = True
		elif cc == 0:
			nosplit = True
		elif debug:
			print("ANOM:", ident, authors, cc, ac)
	if noswap:
		authors = authors.split(", ")
	else:
		authors = authors.split(" and ")
	for idx, author in enumerate(authors):
		if "," in author:
			n = author.split(", ")
			authors[idx] = n[1] + " " + n[0]
		if not ident in authorworks:
			authorworks[ident] = []
		authorworks[ident].append(authors[idx])
	if anom and debug and not noswap and not nosplit:
		print(anom, authorworks[ident])

def xid(s, xids):
	while not s in xids:
		rid = "_S" + str(random.randrange(10000, 100000))
		if not rid in xids:
			xids[rid] = s
			xids[s] = rid
			return rid
	return xids[s]

os.makedirs("graphs", exist_ok=True)
filename_techbib = "graphs/sldgraph-techbib.dot"
f = open(filename_techbib, "w")

xids = {}
print("digraph sldgraph {", file=f)
print("overlap=false;", file=f)
for ident in sorted(analysis):
	for t in analysis[ident]["technologies"]:
		for author in authorworks[ident]:
			print("{} -> {};".format(xid(author, xids), xid(t, xids)), file=f)
for rid in xids:
	if rid.startswith("_"):
		shape = ""
		if xids[rid] in tech:
			color = "e0e0ff"
			if tech[xids[rid]]["open-source"]:
				color = "ffe0e0"
			shape = ",shape=box,style=filled,fillcolor=\"#{}\"".format(color)
		print("{} [label=\"{}\"{}];".format(rid, xids[rid], shape), file=f)
print("}", file=f)
f.close()

filename_bib = "graphs/sldgraph-bib.dot"
f = open(filename_bib, "w")
print("digraph sldgraph {", file=f)
print("overlap=false;", file=f)
for ident in sorted(authorworks):
	for author in authorworks[ident]:
		print("{} -> {};".format(xid(author, xids), xid(ident, xids)), file=f)
for rid in xids:
	if rid.startswith("_") and not xids[rid] in tech:
		shape = ""
		if xids[rid] in biblio:
			color = "a0ffa0"
			shape = ",shape=box,style=filled,fillcolor=\"#{}\"".format(color)
			if "correlation" in base[xids[rid]]:
				color = "d00000"
				print("{} -> {} [style=dotted,color=\"#{}\"];".format(rid, xids[base[xids[rid]]["correlation"]], color), file=f)
		print("{} [label=\"{}\"{}];".format(rid, xids[rid], shape), file=f)
print("}", file=f)
f.close()

def generate_dotfile(filename, fieldname, color):
	xids = {}
	f = open(filename, "w")
	print("digraph sldgraph {", file=f)
	print("overlap=false;", file=f)
	for ident in analysis:
		for field in analysis[ident][fieldname]:
			print("{} -> {};".format(xid(ident, xids), xid(field, xids)), file=f)
	for rid in xids:
		if rid.startswith("_"):
			shape = ""
			if not xids[rid] in analysis:
				shape = ",shape=box,style=filled,fillcolor=\"#{}\"".format(color)
			print("{} [label=\"{}\"{}];".format(rid, xids[rid], shape), file=f)
	print("}", file=f)
	f.close()
	return filename

fn1 = generate_dotfile("graphs/sldgraph-country.dot", "countries", "80d0e0")
fn2 = generate_dotfile("graphs/sldgraph-inst.dot", "institutions", "d0e080")
# TODO: "pos" attributes (https://www.graphviz.org/doc/info/attrs.html#d:pos) to prepare worldmap...
fn3 = generate_dotfile("graphs/sldgraph-fields.dot", "fields", "60b0ff")
fn4 = generate_dotfile("graphs/sldgraph-nature.dot", "nature", "d0d050")
fn5 = generate_dotfile("graphs/sldgraph-tech.dot", "technologies", "a0a0f0")

for filename in (filename_techbib, filename_bib, fn1, fn2, fn3, fn4, fn5):
	# engines: twopi, sfdp, ...
	engine = "sfdp"
	cmd = "{} -Tpdf {} > {}".format(engine, filename, filename + ".pdf")
	os.system(cmd)
	print("Graph: {}".format(filename + ".pdf"))
	print("(Scale: pdfposter -p2x2a4 {}.pdf {}.print.pdf)".format(filename, filename))

os.chdir("graphs")
if os.path.isfile("convert.sh"):
	os.system("sh convert.sh")
else:
	print("Warning: converter script not found")
