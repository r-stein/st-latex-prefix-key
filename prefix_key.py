import sublime
import sublime_plugin


def settings():
    """Return the package settings object."""
    return sublime.load_settings("LaTeXPrefixKey.sublime-settings")


def _is_prefixed(view):
    """Return whether the prefix text is before the cursor."""
    last_prefix = view.settings().get("lpk_insert_prefix", "")
    if not last_prefix:
        return False
    for sel in view.sel():
        if not sel.empty:
            return False

        line = view.line(sel)
        before_str = view.substr(sublime.Region(line.begin(), sel.b))
        if last_prefix not in before_str:
            return False
    return True


def _remove_prefix(view, edit):
    """Delete the prefix text before the cursor."""
    last_prefix = view.settings().get("lpk_insert_prefix", "")

    for sel in view.sel():
        line = view.line(sel)
        before_str = view.substr(sublime.Region(line.begin(), sel.b))
        before_pos = before_str.rindex(last_prefix) + line.begin()
        before_reg = sublime.Region(before_pos, sel.b)
        view.replace(edit, before_reg, "")


def _cancel_timeout(view):
    """Clear the prefix key after a timeout."""
    if hasattr(_cancel_timeout, "previous_callback"):
        _cancel_timeout.previous_callback.enabled = False

    def do_remove_status():
        if do_remove_status.enabled:
            _clear_prefix_key_mode(view)
    do_remove_status.enabled = True
    _cancel_timeout.previous_callback = do_remove_status

    press_time = int(settings().get("key_combination_time") * 1000)
    sublime.set_timeout(do_remove_status, press_time)


def _clear_prefix_key_mode(view):
    """Delete the prefix key settings of the view."""
    view.erase_status("latex_prefix_key.mode")
    view.settings().erase("lpk_insert_prefix")


class LatexPrefixKeyPrefixCommand(sublime_plugin.TextCommand):
    """Insert and activate the prefix key."""
    def run(self, edit, insert_prefix, mode="math"):
        view = self.view
        for sel in view.sel():
            view.insert(edit, sel.b, insert_prefix)

        view.set_status("latex_prefix_key.mode",
                        "Prefix Mode: {0}".format(mode))
        view.settings().set("lpk_insert_prefix", insert_prefix)

        _cancel_timeout(view)


class LatexPrefixKeyCancelCommand(sublime_plugin.TextCommand):
    """Cancel the prefix key mode."""
    def run(self, edit):
        _clear_prefix_key_mode(self.view)


class LatexPrefixKeyInsertCommand(sublime_plugin.TextCommand):
    """Insert the characters and exit prefix key mode."""
    def run(self, edit, characters):
        view = self.view
        _remove_prefix(view, edit)
        view.run_command("insert", {"characters": characters})
        _clear_prefix_key_mode(view)


class LatexPrefixKeyInsertSnippetCommand(sublime_plugin.TextCommand):
    """Insert the snippet and exit prefix key mode."""
    def run(self, edit, contents):
        view = self.view
        _remove_prefix(view, edit)
        view.run_command("insert_snippet", {"contents": contents})
        _clear_prefix_key_mode(view)


class LatexPrefixKeyContext(sublime_plugin.EventListener):
    """Determine which context is active."""
    def _enabled(self, view, mode):
        status = view.get_status("latex_prefix_key.mode")
        is_mode = not mode or status.endswith(" {0}".format(mode))
        enabled = (is_mode and _is_prefixed(view))
        return enabled

    def _math_selector(self, view, selector, operator, operand, match_all):
        scope_selector = settings().get("math_scope_selector")
        quantifier = all if match_all else any
        is_selector = quantifier(view.score_selector(sel.b, scope_selector)
                                 for sel in view.sel())
        return is_selector

    def on_query_context(self, view, selector, operator, operand, match_all):
        if not selector.startswith("latex_prefix_key"):
            return False

        kwargs = locals()
        del kwargs["self"]

        if selector == "latex_prefix_key":
            result = self._enabled(view, None)
        elif selector == "latex_prefix_key.math_selector":
            result = self._math_selector(**kwargs)
        elif selector == "latex_prefix_key.default_prefix_key_enabled":
            result = not settings().get("disable_default_prefix_key")
        elif selector.startswith("latex_prefix_key.mode"):
            split = selector.split(".")
            mode = len(split) >= 3 and split[2] or None
            result = self._enabled(view, mode)
            # special handling for math modes, i.e. just start math modes
            # with "math_"
            if result and mode.startswith("math"):
                result = self._math_selector(**kwargs)

        if operator == sublime.OP_EQUAL:
            result = result == operand
        elif operator == sublime.OP_NOT_EQUAL:
            result = result == operand
        else:
            raise Exception("Unsupported operator {0}".format(operator))

        return result
