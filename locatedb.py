#!/usr/bin/env python
# -*- coding: iso-8859-2 -*-
# $Date: 2007-06-10 21:34:50 $, $Revision: 1.7 $
#
# Library/utility for reading and writing locatedb (v2.0) files.
# Read man locate, man locatedb for details.
# 
# Author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# www:    http://www.mula.w.pl
#
# License: BSD
#

__all__ = ["compress", "decompress"]

from os.path   import join, commonprefix
from itertools import chain


def compress(paths):
	"""Create locatedb file.  Generator yields fragments of locatedb
	file.  Paths is any iterable object of strings."""

	prev_path = ""
	prev_n    = 0
	for path in chain(["LOCATE02"], paths):
		comm = commonprefix([path, prev_path])
		n    = len(comm)
		diff = n - prev_n

		prev_n    = n
		prev_path = path

		bytes = ""

		# encode diff
		if abs(diff) <= 127:
			# diff in [-127..127]
			bytes += chr(diff & 0xff)
		else:
			# diff larger
			bytes += chr(0x80)

			hilo   = diff & 0xffff
			bytes += chr((hilo >> 8) & 0xff)
			bytes += chr(hilo & 0xff)

		# write path fragment
		bytes += path[n:]

		# and finish one with null-char
		bytes += "\x00"

		yield bytes


def decompress_aux(file):
	"""Decompress locatedb file (doesn't check if file is valid!).
	Generator yields all paths, including first dummy-path
	"LOCATE02".  File have to be any file-like object that support
	read."""
	class Dummy: pass

	curr = Dummy()
	curr.buffer = ""
	curr.idx = 0

	def getc():
		# XXX any improvements?
		try:
			c = curr.buffer[curr.idx]
			curr.idx += 1
			return c
		except IndexError:
			curr.buffer = file.read(8192)
			curr.idx    = 0
			if not curr.buffer:
				raise StopIteration
			return getc()


	current_path = ""
	count = 0
	while True:
		diff = ord(getc())
		# decoded diff
		if diff == 0x80:
			diff = ord(getc()) * 256 + ord(getc())
			if diff >= 0x8000:
				diff = -((~diff + 1) & 0xffff)
		elif diff > 0x80:
			diff = -((~diff + 1) & 0xff)

		# read path fragment
		path = ""
		while True:
			c = getc()
			if c == "\x00":
				break
			else:
				path += c

		# get length of path prefix from previous iteration
		count += diff

		# and create real path
		current_path = current_path[:count] + path
		yield current_path


def decompress(file):
	"""Decompress locatedb file."""
	iter = decompress_aux(file)
	try:
		first_entry = iter.next()
	except StopIteration:
		raise ValueError("Not a locate v.2 file")

	if first_entry != "LOCATE02":
		raise ValueError("Not a locate v.2 file")

	for item in iter:
		yield item


usage_text = """\
Utility to read/write locatedb 2.0 files.

usage:
	%s decompress infile
	%s compress path outfile
	%s compress-list infile outfile

decompres     - print on stdout decompressed contents of infile 
compress      - create locatedb file for given path
compress-list - create locatedb from arbitrary list of paths
                that are readed from infile

If infile/outfile is "-" or "--" then file is associated with stdin/stdout.
"""

if __name__ == "__main__":
	import os, os.path, sys

	def usage(onerror=False):
		name = sys.argv[0]
		sys.stdout.write(usage_text % (name, name, name))
		if onerror:
			sys.exit(1)
		else:
			sys.exit(0)

	def get_option(index, default=None):
		try:
			return sys.argv[index]
		except IndexError:
			if type(default) is not str:
				usage(True)
			else:
				return default

	def die(*info):
		for text in info:
			sys.stderr.write(str(text))
			sys.stderr.write(" ")
		else:
			sys.stderr.write("\n")

		sys.exit(1)

	action = get_option(1).lower()

	###
	if action == "compress":

		path    = get_option(2)
		outfile = get_option(3, "-")

		if not os.path.exists(path):
			die("Directory", path, "doesn't exists")
		elif not os.path.isdir(path):
			die("File", path, "is not directory")

		if outfile in ["-", "--"]:
			outfile = sys.stdout
		elif os.path.exists(outfile):
			die("File", outfile, "already exists")
		else:
			outfile = open(outfile, "wb")

		def iter_dir_tree(root):
			for dirname, directories, files in os.walk(root):
				for file in files:
					yield join(dirname, file)

		for fragment in compress(iter_dir_tree(path)):
			outfile.write(fragment)

		if outfile is not sys.stdout:
			file.close()


	###
	elif action == "compress-list":

		infile_name  = get_option(2, "-")
		outfile_name = get_option(3, "-")

		if infile_name in ["-", "--"]:
			infile = sys.stdin
		else:
			if not os.path.exists(infile_name):
				die("File", infile_name, "doesn't exists")
			infile = open(infile_name, "r")

		if outfile_name in ["-", "--"]:
			outfile = sys.stdout
		else:
			if os.path.exists(outfile_name):
				die("File", outfile_name, "already exists")
			outfile = open(outfile_name, "wb")

		def iter_lines(file):
			for line in file:
				yield line[:-1]

		for fragment in compress(iter_lines(infile)):
			outfile.write(fragment)

		if infile_name is not sys.stdin:
			infile.close()
		if outfile_name is not sys.stdout:
			outfile.close()

	###
	elif action == "decompress":

		infile = get_option(2, "-")
		if infile in ["-", "--"]:
			infile = sys.stdin
		else:
			if not os.path.exists(infile):
				die("File", outfile, "doesn't exists")
			infile = open(infile, "rb")

		for path in decompress(infile):
			print path

		if infile is not sys.stdin:
			infile.close()
	else:
		usage(True)

# vim: ts=4 sw=4 nowrap noexpandtab
