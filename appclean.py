#!/usr/bin/python2
#muddled together by lain, use at your own risk
import os
import copy

defaultdesktopfiles = list()
desktopfiles = list()
rootdir = os.path.expanduser("~/.local/share/")
rootapplications = "/usr/share/applications/"
userapplications = rootdir + "applications/"
trash = rootdir + "trash/"

def parseFile(f):
	r = open(f)
	cont = dict()
	heading = False
	for line in r:
		if line.strip() == '' or line.startswith('#'):
			continue
		if not heading:
			if line.strip() != '[Desktop Entry]':
				print('Invalid .desktop file '+f)
				return None
			else:
				heading = True
		else:
			line = line.split('=',1)
			if(len(line)==2):
				key = line[0].strip()
				value = line[1].strip()
				cont[key]=value
	r.close()
	return [f,cont]

def parseDesktopFiles(appdir, l):
	for f in os.listdir(appdir):
		f = appdir + f
		if os.path.isdir(f) == True:
			parseDesktopFiles(f+"/", l)
		elif f.endswith('.desktop'):
			ret = parseFile(f)
			if ret != None:
				l.append(ret)

def appcontains(app, l):
	for app2 in l:
		if app!=app2 and app[1]['Exec']==app2[1]['Exec']:
			return app2
	return False

def fixdup(app,dup):
	print("Merging duplicate entry:")
	print(app[0])
	print(dup[0])
	newmime = set(app[1].get('MimeType','').split(';') + dup[1].get('MimeType','').split(';'))
	newmime.remove('')
	dup[1]['MimeType'] = ';'.join(newmime)
	app[1] = dict(app[1].items() + dup[1].items())
	desktopfiles.remove(dup)
		
def unduplicate():
	for app in desktopfiles:
		if isWine(app): 
			continue
		dup = appcontains(app, desktopfiles)
		if dup:
			fixdup(app,dup)
		dup = appcontains(app, defaultdesktopfiles)
		if dup:
			fixdup(dup,app)

def toSaneName(app):
	fname = os.path.basename(app[0])
	if fname.startswith('wine-extension-'):
		return fname[15:-8].upper()

	mimetype = app[1]['MimeType'].split(';')[0]
	if mimetype == 'text/plain':
		return 'Textfile'
	if 'image/' in mimetype:
		return mimetype.split('/')[1].upper()
	if '-extension-' in mimetype:
		return mimetype.split('-extension-')[1].upper()
	if mimetype.startswith('application/'):
		mimetype = mimetype[12:]
		
	return None

def isWine(app):
	ex = app[1]['Exec']
	return 'env WINEPREFIX="' in ex and '" wine start /ProgIDOpen' in ex

def fixWine():
	for app in desktopfiles:
		if(isWine(app)):
			name = toSaneName(app)
			if name:
				oldname = app[1]['Name']
				app[1]['Name'] = 'Open '+name+'-File with Wine'
				print('Rename: '+oldname + " -> "+app[1]['Name'])

def removeDesktopFiles():
	for app in desktopfilescopy:
		os.remove(app[0])

def writeDesktopFiles():
	for app in desktopfiles:
		handle = open(app[0],'w')
		handle.write('[Desktop Entry]\n')
		for key,value in app[1].items():
			handle.write(key+'='+value+'\n')
		handle.close()
		
print(" - Parsing applications...")
parseDesktopFiles(userapplications, desktopfiles)
parseDesktopFiles(rootapplications, defaultdesktopfiles)
desktopfilescopy = copy.deepcopy(desktopfiles)

print("\n - Finding duplicates...")
unduplicate()

print("\n - Fixing Wine's desktop files...")
fixWine()

#Lets do this 
print("\n - Removing old files...")
removeDesktopFiles()
print(" - Writing new ones...")
writeDesktopFiles() 
print(" - Done!\n")
