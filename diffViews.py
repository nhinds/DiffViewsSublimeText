import sublime, sublime_plugin
import difflib
import os

def viewToString(view):
	if view.name() is not None and len(view.name()) > 0:
		return view.name()
	if view.file_name() is not None and len(view.file_name()) > 0:
		return view.file_name()
	return '?? Untitled ??'

def performDiff(window, viewA, viewB, regionA=None, regionB=None):
	if regionA is None:
		regionA = sublime.Region(0, viewA.size())
	if regionB is None:
		regionB = sublime.Region(0, viewB.size())

	aName = viewToString(viewA)
	bName = viewToString(viewB)

	leftLines = viewA.substr(regionA).splitlines()
	rightLines = viewB.substr(regionB).splitlines()

	diff = difflib.unified_diff(leftLines, rightLines, aName, bName,lineterm='')

	difftxt = '\n'.join(line for line in diff)

	if difftxt == "":
		sublime.status_message("Files are identical")
	else:
		v = window.new_file()
		v.set_name('Diff: ' + os.path.basename(aName) + " -> " + os.path.basename(bName))
		v.set_scratch(True)
		v.set_syntax_file('Packages/Diff/Diff.tmLanguage')
		v.run_command('set_content_to_view', {'difftxt': difftxt})

class SetContentToViewCommand(sublime_plugin.TextCommand):
	def run(self, edit, difftxt):
		self.view.insert(edit, 0, difftxt)

class DiffViewsCommand(sublime_plugin.WindowCommand):
	def run(self):
		if self.window.active_view() is None:
			sublime.status_message('No active view to diff!')
			return
		views = []
		for view in self.window.views():
			views.append(viewToString(view))
		self.window.show_quick_panel(views, self._onSelect)

	def _onSelect(self, index):
		if index < 0:
			return

		viewA = self.window.active_view()
		viewB = self.window.views()[index]

		performDiff(self.window, viewA, viewB)

		
class DiffSelectionsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if len(self.view.sel()) != 2:
			return
		performDiff(self.view.window(), self.view, self.view, self.view.sel()[0], self.view.sel()[1])
		
	def is_enabled(self):
		return len(self.view.sel()) == 2

	def is_visible(self):
		return self.is_enabled()
