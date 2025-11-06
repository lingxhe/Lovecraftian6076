"""Markdown logging utility for chat sessions"""
import os
import sys
from datetime import datetime
from typing import Optional
import streamlit as st


class ChatLogger:
	"""Log chat messages and system prints to markdown file"""
	
	def __init__(self, log_dir: str = "logs"):
		self.log_dir = log_dir
		self.log_file: Optional[str] = None
		self.original_print = print
		self.original_stdout = sys.stdout
		self.log_buffer: list = []
		self.enabled = True
		
		# Create logs directory if it doesn't exist
		os.makedirs(log_dir, exist_ok=True)
	
	def start_session(self, character_name: str = "Unknown") -> str:
		"""Start a new logging session and return log file path"""
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
		filename = f"{timestamp}_{safe_name}.md"
		self.log_file = os.path.join(self.log_dir, filename)
		
		# Write header
		with open(self.log_file, 'w', encoding='utf-8') as f:
			f.write(f"# Chat Session Log\n\n")
			f.write(f"**Character:** {character_name}\n")
			f.write(f"**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
			f.write("---\n\n")
		
		return self.log_file
	
	def log_message(self, role: str, content: str, scene: Optional[str] = None):
		"""Log a chat message"""
		if not self.log_file:
			return
		
		try:
			with open(self.log_file, 'a', encoding='utf-8') as f:
				# Different formatting for player vs keeper
				if role == "user":
					f.write(f"## 👤 Player\n\n")
					f.write(f"{content}\n\n")
				elif role == "assistant":
					f.write(f"## 🎭 Keeper")
					if scene:
						f.write(f" *(Scene: {scene})*")
					f.write(f"\n\n{content}\n\n")
				
				f.write("---\n\n")
		except Exception as e:
			# Silently fail if logging fails
			pass
	
	def log_system(self, message: str):
		"""Log system/debug message"""
		if not self.log_file:
			return
		
		try:
			with open(self.log_file, 'a', encoding='utf-8') as f:
				f.write(f"### 🔧 System\n\n")
				f.write(f"```\n{message}\n```\n\n")
		except Exception:
			pass
	
	def log_tool_call(self, tool_name: str, args: dict, result: Optional[str] = None):
		"""Log tool call information"""
		if not self.log_file:
			return
		
		try:
			with open(self.log_file, 'a', encoding='utf-8') as f:
				f.write(f"### 🛠️ Tool: {tool_name}\n\n")
				f.write(f"**Arguments:**\n```json\n{args}\n```\n\n")
				if result:
					f.write(f"**Result:**\n```\n{result[:200]}...\n```\n\n")
				f.write("---\n\n")
		except Exception:
			pass
	
	def log_print(self, *args, **kwargs):
		"""Intercept print calls and log them"""
		# Call original print first
		self.original_print(*args, **kwargs)
		
		# Also log to file
		if self.log_file and self.enabled:
			try:
				message = ' '.join(str(arg) for arg in args)
				with open(self.log_file, 'a', encoding='utf-8') as f:
					f.write(f"### 🔧 System Output\n\n")
					f.write(f"```\n{message}\n```\n\n")
			except Exception:
				pass
	
	def close(self):
		"""Close the logging session"""
		if self.log_file:
			try:
				with open(self.log_file, 'a', encoding='utf-8') as f:
					f.write(f"\n\n**Session ended:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
			except Exception:
				pass
			self.log_file = None


# Global logger instance
_logger: Optional[ChatLogger] = None
_original_print = None


def get_logger() -> Optional[ChatLogger]:
	"""Get the global logger instance"""
	return _logger


def init_logger(character_name: str = "Unknown", enable_print_capture: bool = True) -> ChatLogger:
	"""Initialize global logger and optionally capture print output"""
	global _logger, _original_print
	
	_logger = ChatLogger()
	log_file = _logger.start_session(character_name)
	
	# Replace print function to also log to file
	if enable_print_capture:
		try:
			import builtins
			_original_print = builtins.print
			
			def logged_print(*args, **kwargs):
				_original_print(*args, **kwargs)
				if _logger:
					_logger.log_print(*args, **kwargs)
			
			builtins.print = logged_print
		except Exception:
			# If we can't replace print, just continue without print capture
			pass
	
	return _logger


def stop_logger():
	"""Stop logging and restore original print"""
	global _logger, _original_print
	if _logger:
		_logger.close()
		_logger = None
	if _original_print:
		__builtins__['print'] = _original_print
		_original_print = None


def log_message(role: str, content: str, scene: Optional[str] = None):
	"""Log a message using global logger"""
	if _logger:
		_logger.log_message(role, content, scene)


def log_system(message: str):
	"""Log system message using global logger"""
	if _logger:
		_logger.log_system(message)


def log_tool_call(tool_name: str, args: dict, result: Optional[str] = None):
	"""Log tool call using global logger"""
	if _logger:
		_logger.log_tool_call(tool_name, args, result)

