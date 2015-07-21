# -*- coding: utf-8 -*-
import os
import sys
import time
import psutil
import random
import serial
import signal
import socket
import threading
import subprocess
from gi.repository import Notify


music_root = "/_/nfs/arch_desktop/music"
exclude_dir = ["Misc", "Live", "Symphonies", ".Trash-1000", ".git"]
favorite = []
#favorite_list = []
favorite_list = [["Chiptune"],							#0
				["Pink.Floyd"],
				["Classical", "Beethoven", "Mozart"],	#2
				["Metallica"],
				["Jimi.Hendrix"],						#4
				["Donovan"],
				["Queen"],								#6
				["Donovan", "Iron.Butterfly", "60's", "Iggy.Pop", "The.Doors", "The.Animals",
				 "Jefferson.Airplane", "The.Who", "Jimi.Hendrix", "The.Mamas&The.Papas"],
				["Mix"],								#8
				["Led.Zeppelin", "Portishead"],
				["The.Doors"], 							#10
				["Iron.Butterfly"]]						#11		
nb_favorite = 11
choose_favorite = 11

player = "vlc"
#player_arg = ["--no-loop", "--play-and-exit", "--quiet",
# "--qt-minimal-view", "--no-overlay", "--no-qt-video-autoresize"]
player_arg = ["--no-loop", "--play-and-exit",
 "--quiet", "--no-overlay", "--no-qt-video-autoresize"]
list_ext = [".flac", ".ogg", ".ogv", ".mp3", ".mp4", ".webm"]
replay = True
list_played = []
is_playing = False
has_played = False
is_paused = False
#mode = "all"

class MusicProcess(object):
	def __init__(self):
		global choose_favorite
		self.is_playing = True
#		self.has_played = has_played
#		if not self.has_played: 
#			self.choose_favorite = choose_favorite
		self.file_list = get_file_list(choose_favorite)
		self.is_prev_music = False
		self.continue_playing = True
		self.player_process = None
		self.player_pid = None
#		print(self.file_list)
		self.music_thread = threading.Thread(target=self.play_random_music)
		self.music_thread.daemon = True
		self.music_thread.start()
#		self.has_played = True
		
	def play_random_music(self):
		print("Hello, this is the thread")
		print("File list: %s" % self.file_list)
		self.list_played = []
		while self.continue_playing:
			if self.player_process is None:
				if self.is_prev_music: 
					self.random_file = self.last_music
					print("===IS PREV")
					print(self.list_played)
					self.is_prev_music = False
				else: 
					self.random_file = random.choice(self.file_list)
					if set(self.list_played) == set(self.file_list):
						self.list_played = []
						print("\n\nREMOVING PLAYED LIST\n\n")
					
					while self.random_file in self.list_played:
						self.random_file = random.choice(self.file_list)
					self.list_played.append(self.random_file)
					print("===IS NOT PREV")
					print(self.list_played)
				
#				random_file = random.choice(self.file_list)
				print("\nPlaying: ", self.random_file)
				self.player_process = subprocess.Popen([player, self.random_file] + player_arg)
				self.player_pid = int(self.player_process.pid)
				print("PID: %d" % self.player_pid)
			if self.player_process is not None: 
				self.player_process.wait()
			print("LOOP")
			self.player_process = None
		print("End of: ", self.random_file)
		self.is_prev_music = False

	
	
	def kill_proc(self):
		print("Killing proc")
		self.continue_playing = False
		self.player_process = None
		if self.player_pid is not None:
			print("Player PID to be killed: ", self.player_pid)
			os.kill(self.player_pid, 9)
		self.player_pid = None
		is_playing = False
		self.is_prev_music = False
	
	
	def play_music(self):
		global is_paused 
		if is_paused:
			print("Restarting Music")
			self.p.resume()
			is_paused = False
		else:
			print("Suspending Music")
			if self.player_pid is not None:
				print("Player PID to be suspended: ", self.player_pid)
				self.p = psutil.Process(self.player_pid)
				self.p.suspend()
				is_paused = True
			else:
				print("Player PID is not set")
	
	
	def prev_music(self):
		print("Previous Music=>")
		self.player_process = None
		if self.player_pid is not None:
			print("Player PID to be killed: ", self.player_pid)
			os.kill(self.player_pid, 9)
		self.player_pid = None
		if self.list_played: 
			self.last_music = self.list_played.pop(-1)
			print("Last Music: %s" % self.last_music)
			self.is_prev_music = True
	
	
	def next_music(self):
		print("Next Music=>")
		self.player_process = None
		if self.player_pid is not None:
			print("Player PID to be killed: ", self.player_pid)
			os.kill(self.player_pid, 9)
		self.player_pid = None
		self.is_prev_music = False
	

	def select_music(self):
		global choose_favorite
		choose_favorite = choose_favorite + 1
		if choose_favorite > nb_favorite: 
			choose_favorite = 0
		print("Selected favorite: %d" % choose_favorite)
		print("Selected: %s" % favorite_list[choose_favorite])
#		choose_favorite = self.choose_favorite


def get_file_list(choose_favorite):
	nb_arg = len(sys.argv)
	
	if choose_favorite <= nb_favorite:
#		if str(sys.argv[1]) == "l":
#			for i, item in enumerate(favorite_list):
#				print("N°%02d -> %s" % (i, item))
#			os._exit(1)
			
#		arg = int(sys.argv[1])
#		print("ARG: ", arg)
		favorite = favorite_list[choose_favorite]
		print("FAVORITE: ", favorite)
		mode = "favorite"
	else:
		mode = "all"
		
	file_list = []
	
	print("Music root: %s" % music_root)

	if mode == 'favorite':
		for fav in favorite:
			favorite_dir = os.path.join(music_root, fav)
			print("Favorite dir: %s" % favorite_dir)
			for dirname, dirnames, filenames in os.walk(favorite_dir):
				exclude = False
				for excl_dir in exclude_dir: 
					if excl_dir in dirname: 
						print("EXCLUDE: ", dirname)
						exclude = True
				if not exclude: 
					print("DIRNAME: ", dirname)
					print ("DIRNAMES: ", dirnames)
					print ("FILENAMES: ", filenames)
					for filename in filenames:
						file_ext = os.path.splitext(filename)[1].lower()
						for ext in list_ext: 
							if(file_ext == ext):
								file_list.append(os.path.join(dirname, filename))
	else:
		for root in music_root:
			print(os.listdir(root))

			for dirname, dirnames, filenames in os.walk(root):

			#	for subdirname in dirnames:
			#		print os.path.join(dirname, subdirname)
	#			print "DIRNAME: ", dirname
		#		print "DIRNAMES: ", dirnames
		#		print "FILENAMES: ", filenames
	#			print 'Number of arguments: ', 
	#			print 'Argument List:', str(sys.argv)
		
				curr_dir = os.path.basename(dirname)
				if curr_dir in exclude_dir:
					print("EXCLUDE: ", curr_dir)
				else:
					if mode == "all":
						for filename in filenames:
							file_ext = os.path.splitext(filename)[1].lower()
							for ext in list_ext: 
								if(file_ext == ext):
									file_list.append(os.path.join(dirname, filename))

					else:
						if curr_dir in favorite:
		#					print "DIRNAMES: ", dirnames
							for dir_name in dirnames:
								favorite.append(dir_name)
		#					print "FAV: ", favorite_3
							for filename in filenames:
									file_ext = os.path.splitext(filename)[1].lower()
									for ext in list_ext: 
										if(file_ext == ext):
											file_list.append(os.path.join(dirname, filename))

				if '.git' in dirnames:
					dirnames.remove('.git')
	return file_list

#get_file_list()

#def play_random_music():
#	file_list = get_file_list()
#	print(file_list)
#	list_played = []
#	global play_process
##	global shutdown_flag
#	while replay:
#		random_file = random.choice(file_list)
#		if set(list_played) == set(file_list):
#			list_played = []
#			print "\n\nREMOVING PLAYED LIST, DO YOU SEE THIS MESSAGE ? IS IT BIG ENOUGH ??\n\n"
#		while random_file in list_played:
#			random_file = random.choice(file_list)
#		list_played.append(random_file)
#		print "\nPlaying: ", random_file
#		Notify.init("What do I write here ?")
#		Notify.Notification.new("Playing", os.path.basename(random_file), "dialog-information").show()

##		subprocess.call(["notify-send", "Playing: ", os.path.basename(random_file)])
#		if play_process is None:
#			play_process = subprocess.Popen([player, random_file] + player_arg)
##			print "VLC_PID:", play_process.pid
#			client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#			client_socket.connect(('192.168.1.999', 9999))
#			vlc_pid = "VLC_PID:%s" % str(play_process.pid)
#			client_socket.send(vlc_pid)
#		if play_process is not None:
#			play_process.wait()
##			return play_process		
#		print "End of: ", random_file
#		print "Played: %s musics" % len(list_played)
#		play_process = None
#	if play_process is not None:
#		print "\nMusic is off"
		


if __name__ == "__main__":
	print("Music server controlled from serial")
	ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
	while True:
		line = ser.readline()
		line = str(line, "ascii").rstrip('\r\n')
#		if not line:
#			print("Empty")
		if line:
			print(line)
			if "start_music" in line:
				print("==Starting Music")
				music_proc_mgr = MusicProcess()
				is_playing = True
			if is_playing:
				if "stop_music" in line:
					print("==Stopping Music")
					music_proc_mgr.kill_proc()
				elif "play_music" in line:
					print("==Playing Music")
					music_proc_mgr.play_music()
				elif "prev_music" in line:
					print("==Previous Music")
					music_proc_mgr.prev_music()
				elif "next_music" in line:
					print("==Next Music")
					music_proc_mgr.next_music()
			if "select_music" in line:
				print("==Selecting Music")
				music_proc_mgr.select_music()

	ser.close()

#play_random_music()





