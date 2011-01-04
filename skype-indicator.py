#!/usr/bin/env python
#
#Copyright 2010 Jonathan Foucher
#
#Authors:
#    Jonathan Foucher <jfoucher@6px.eu>
#
#This program is free software: you can redistribute it and/or modify it 
#under the terms of either or both of the following licenses:
#
#1) the GNU Lesser General Public License version 3, as published by the 
#Free Software Foundation; and/or
#2) the GNU Lesser General Public License version 2.1, as published by 
#the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the applicable version of the GNU Lesser General Public 
#License for more details.
#
#You should have received a copy of both the GNU Lesser General Public 
#License version 3 and version 2.1 along with this program.  If not, see 
#<http://www.gnu.org/licenses/>
#


import indicate
import gobject
import pynotify
import gtk
import hashlib
import Skype4Py
import urllib
import sys
import os


class skypeIndicator:
	notifShown={}
	oldcount={}
	count={}
	indicator={}
	def __init__(self):
		# get skype control
		self.skype= Skype4Py.Skype()
		try:
			if not self.skype.Client.IsRunning:
				self.skype.Client.Start()
		except:
			print "Please open skype first"
			#gtk.main_quit()
			sys.exit(-1)
		try:
			self.skype.Attach()
		except:
			print "Please open skype first"
			#gtk.main_quit()
			sys.exit(-1)

		


		#create notification icon

		self.server = indicate.indicate_server_ref_default()
		self.server.set_type("message.im")
		self.server.set_desktop_file("/usr/share/applications/skype.desktop")
		self.server.connect("server-display", self.server_display)
		#self.server.set_status (indicate.STATUS_ACTIVE)
		self.server.show()
#		for slot in dir(self.server):
#			attr = getattr(self.server, slot)
#			print attr

		#self.unread={}
		#self.indicator.set_property('draw-attention', 'true');
		self.create_indicators()
		#pass
		#indicator.connect("user-display", self.display_msg)

	def create_indicators(self):

		self.count={}
		self.get_messages()
		for name in self.unread:

			msg=self.unread[name][0]

			if name not in self.count:
				self.count[name]=0
			if name not in self.oldcount:
				self.oldcount[name]=0

			if not name in self.indicator:
				self.indicator[name] = indicate.Indicator()
				print "creating indicator"
	#			for slot in dir(self.indicator[name]):
	#				attr = getattr(self.indicator[name], slot)
	#				print attr
				self.fullname=self.name_from_handle(name)
				self.indicator[name].set_property("subtype", "im")
				self.indicator[name].set_property("sender", self.fullname )
				self.indicator[name].set_property("handle", name)
				user=self.user_from_handle(name)


				try:
					self.file=name + '.jpg'
					user.SaveAvatarToFile(file)
				except Skype4Py.errors.ISkypeError:
					h=hashlib.md5(name).hexdigest()
					urllib.urlretrieve('http://friedcellcollective.net/monsterid/monster/%s/64' % h,name + 'jpg')
					self.file=name + 'jpg'

				pixbuf=gtk.gdk.pixbuf_new_from_file(self.file)
				self.indicator[name].set_property_icon("icon", pixbuf)


				self.indicator[name].set_property_time("time", msg.Timestamp)
				self.indicator[name].show()
				self.indicator[name].connect("user-display", self.display_msg)
				
			msgbody = ''
			for eachmsg in self.unread[name][::-1]:
				msgbody += eachmsg.Body + "\n"
			self.indicator[name].set_property("body", msgbody)
			if self.count[name] > 1:
				self.indicator[name].set_property("count", str(self.count[name]))
			



			if self.count[name] > self.oldcount[name]:
				self.notifShown[name]=False

			if not self.notifShown.get(name, False) and self.showNotification(self.fullname, msgbody, self.file):
				self.notifShown[name]=True
				self.indicator[name].set_property("draw-attention", "true")
				self.indicator[name].show()
				print "notification shown for", name

			print "%d messages from %s" %(self.count[name],name)
				
			#print self.indicator[name].get_property("sender")

		self.oldcount=self.count
		return True
		#print name

	def name_from_handle(self,handle):
		user=self.skype.User(handle)
		if user.FullName:
			return user.FullName
		elif user.DisplayName:
			return user.DisplayName
		else:
			return handle

	def user_from_handle(self,handle):
		return self.skype.User(handle)

	def showNotification(self, title, message,file=None):
		'''takes a title and a message to display the email notification. Returns the
        created notification object'''

		n = pynotify.Notification(title, message, "notification-message-im")
		n.set_property("icon-name",os.getcwd() + "/" + file)
		n.show()

		return n

	def get_messages(self):
		print "checking messages"
		self.unread={}

		#print self.skype.MissedMessages
		for msg in self.skype.MissedMessages:
			display_name = msg.FromHandle
			if display_name not in self.count:
				self.count[display_name]=0



			if not display_name in self.unread:
				self.unread[display_name]=[]
			
			self.unread[display_name].append(msg)
			self.count[display_name]+=1
		#print self.unread
		return self.unread



	def server_display(self, widget, timestamp=None):
		self.skype.Client.Focus()

	def display_msg(self, indicator, timestamp):
		indicator.hide()
		indicator.set_property("draw-attention", "false")
		self.skype.Client.OpenMessageDialog(indicator.get_property("handle"))
		print indicator.get_property("body")


if __name__ == "__main__":
	
	skypeind=skypeIndicator()

	# Loop
	gobject.timeout_add_seconds(5, skypeind.create_indicators)
	gtk.main()