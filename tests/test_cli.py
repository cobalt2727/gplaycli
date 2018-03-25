import os
import sys
import hashlib
import subprocess as sp

TESTAPK='org.mozilla.focus'
UPDATEAPK=os.path.join("tests", "com.duckduckgo.mobile.android_3.0.17.apk")
TOKENFILE=os.path.expanduser('~/.cache/gplaycli/token')

def call(args):
	proc = sp.run(args.split(), stdout=sp.PIPE, stderr=sp.PIPE)
	print(proc.stdout.decode(), file=sys.stdout)
	print(proc.stderr.decode(), file=sys.stderr)
	return proc

def stdout_lines(args):
	return (call(args)
			.stdout
			.decode(errors='replace')
			.splitlines(True)
			)

def download_apk():
	call("gplaycli -vd %s" % TESTAPK)

def checksum(apk):
	return hashlib.sha256(open(apk, 'rb').read()).hexdigest()

def test_download():
	if os.path.isfile(TOKENFILE):
		os.remove(TOKENFILE)
	download_apk()
	assert os.path.isfile("%s.apk" % TESTAPK)

def test_alter_token():
	token = open(TOKENFILE).read()
	token = ' ' + token[1:]
	with open(TOKENFILE, 'w') as outfile:
		print(token, file=outfile)
	download_apk()
	assert os.path.isfile("%s.apk" % TESTAPK)

def test_update(apk=UPDATEAPK):
	before = checksum(apk)
	call("gplaycli -vyu tests")
	after = checksum(apk)
	assert after != before

def test_search(string='fire', number=30):
	outlines = stdout_lines("gplaycli -s %s -n %d" % (string, number))
	assert len(outlines) <= number + 1

def test_search2(string='com.yogavpn'):
	outlines = stdout_lines("gplaycli -s %s" % string)
	assert len(outlines) >= 0

def test_search3(string='com.yogavpn', number=15):
	outlines = stdout_lines("gplaycli -s %s -n %d" % (string, number))
	assert len(outlines) <= number + 1

def test_another_device(device='hammerhead'):
	call("gplaycli -vd %s -dc %s" % (TESTAPK, device))
	assert os.path.isfile("%s.apk" % TESTAPK)

def test_download_additional_files(apk='com.mapswithme.maps.pro'):
	call("gplaycli -d %s -a" % apk)
	assert os.path.isfile("%s.apk" % apk)
	files = [f for f in os.listdir() if os.path.isfile(f)]
	assert any([f.endswith('%s.obb' % apk) and f.startswith('main') for f in files])
	assert any([f.endswith('%s.obb' % apk) and f.startswith('patch') for f in files])