import re

import sublime
import sublime_plugin

from .prefix_key import _is_prefixed, _remove_prefix


def _is_insert_key(entry):
    return entry.get("command", "") in ["latex_prefix_key_insert",
                                        "latex_prefix_key_insert_snippet"]


def _create_entry(keybinding):
    is_snippet = (keybinding.get("command", "") ==
                  "latex_prefix_key_insert_snippet")

    args = keybinding.get("args", {})
    if not is_snippet:
        characters = args.get("characters", "")
        contents = characters
    else:
        contents = args.get("contents", "")
        characters = contents.replace("{", "")
        characters = re.sub(r"\{[^\}]*\}", "", contents)
        characters = re.sub(r"\$\w+", "", characters)
    entry = {
        "characters": characters,
        "contents": contents,
        "is_snippet": is_snippet,
        "kbd": ",".join(keybinding.get("keys", []))
    }
    return entry


def _load_resource(path):
    return sublime.decode_value(sublime.load_resource(path))


class LatexPrefixKeyHelpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        window = view.window()
        current_mode = view.get_status("latex_prefix_key.mode")
        current_mode = current_mode.lstrip("Prefix Mode: ").strip()

        if _is_prefixed:
            _remove_prefix(view, edit)

        plat = sublime.platform()
        plat = plat.upper() if plat == "osx" else plat.title()

        default_keymap = _load_resource(
            "Packages/LaTeXMathKeys/Default.sublime-keymap")

        user_keymap = []
        for user_path in [
            "Packages/User/Default ({0}).sublime-keymap".format(plat),
            "Packages/User/Default.sublime-keymap"
        ]:
            try:
                user_keymap.extend(_load_resource(user_path))
            except:
                print("Error loading keymap '{0}'".format(user_path))

        selector_name = "latex_prefix_key.mode.{0}".format(current_mode)

        def is_correct_mode(entry):
            return any(e.get("key", "") == selector_name
                       for e in entry.get("context", []))
        keymap = user_keymap + default_keymap
        keymap = list(filter(is_correct_mode, filter(_is_insert_key, keymap)))

        entries = list(map(_create_entry, keymap))
        used_kbd = []
        for entry in entries:
            if entry["kbd"] in used_kbd:
                entry["kbd"] = "({0})".format(entry["kbd"])
            else:
                used_kbd.append(entry["kbd"])

        symbol_map = _load_resource(
            "Packages/LaTeXMathKeys/tex_command_symbol_mapping.json")

        def process_entry(entry):
            characters = entry["characters"]
            contents = entry["contents"]
            name = (characters[1:] if characters[0] == "\\"
                    else characters).title()
            if characters in symbol_map and symbol_map[characters] is not None:
                symbol = symbol_map[characters]
                symbol_str = " ({symbol})".format(**locals())
                show = "{name}{symbol_str}: {contents}".format(**locals())
            else:
                symbol_str = ""
                show = characters
            show = "{name}{symbol_str}: {contents}".format(**locals())
            return [show, entry["kbd"]]
        items = list(map(process_entry, entries))

        def on_done(index):
            if index == -1:
                return
            entry = entries[index]
            if entry["is_snippet"]:
                view.run_command("insert_snippet",
                                 {"contents": entry["contents"]})
            else:
                view.run_command("insert", {"characters": entry["characters"]})
        window.show_quick_panel(items, on_done)
