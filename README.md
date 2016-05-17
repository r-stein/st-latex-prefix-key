# LaTeX Prefix Key

This package creates a prefix key similar to Emacs Auctex. Just press the prefix key followed by keybinding to insert text into the view. E.g. you can press `;` *(prefix key)* and `a` to insert `\alpha`. In addition this packages gives you the possibility to insert your own prefix key and keybindings.
Although it is made for LaTeX and focuses on inserting math commands, you can add your prefix key for other languages as well.


## Usage

Press the prefix key, and a key of the prefix keymap to insert the corresponding command, characters or snippet into the view:

![prefix_key_demo](https://cloud.githubusercontent.com/assets/12573621/15333937/2523766c-1c6c-11e6-87a9-a084e2bb83c9.gif)

You can press the prefix key followed by `?` to get an overview over all available commands in the prefix keymap:

![prefix_key_help_demo](https://cloud.githubusercontent.com/assets/12573621/15333924/0ffbed46-1c6c-11e6-9560-d4b1cdca2114.gif)


### Adding commands to the prefix keymap

The prefix keymaps are handled using contexts. Hence you can add keys by defining a keybinding using the corresponding context. The context key for math mode is `latex_prefix_key.mode.math`.
An example keybinding to insert `\alpha` when pressing `a`:

``` js
{
    "keys": ["a"], "command": "latex_prefix_key_insert", "args": { "characters": "\\alpha" },
    "context":
    [
        { "key": "selector", "operator": "equal", "operand": "text.tex" },
        { "key": "latex_prefix_key.mode.math" }
    ]
},
```

An example keybinding to insert the snippet `"\\mathfrak{$1}$0"` when pressing `c` and then `f`:

``` js
{
    "keys": ["c", "f"], "command": "latex_prefix_key_insert_snippet", "args": {"contents": "\\mathfrak{$1}$0"},
    "context":
    [
        { "key": "selector", "operator": "equal", "operand": "text.tex" },
        { "key": "latex_prefix_key.mode.math" }
    ]
},
```

If you add an addition keymap for an other prefix mode you can replace `math` with the mode name.


### Changing the prefix key

*Disable the default prefix key:*
To disable the default prefix key open the LaTeXMathKeys settings and set the entry `disable_default_prefix_key` to `true`.

*Adding your prefix key:*
Add this keybinding to your user keybinding and replace `#` with the key you want to use as prefix key:

``` js
{
    "keys": ["#"], "command": "latex_prefix_key_prefix",
    "args": { "insert_prefix": "#", "mode": "math"},
    "context":
    [
        { "key": "selector", "operator": "equal", "operand": "text.tex" },
        { "key": "latex_prefix_key.math_selector" }
    ]
},
```


### Adding your own prefix key

A prefix key is bound to a so called `mode`. Select a mode name for your prefix key, it should be unique and `underscore_separated`. If it is prefixed with `math` the corresponding keybinding will only applied inside math scopes.

Add the prefix keybinding to your keymap:

``` js
{
    "keys": ["#"], "command": "latex_prefix_key_prefix",
    "args": { "insert_prefix": "#", "mode": "your_mode"},
    "context":
    [
        { "key": "selector", "operator": "equal", "operand": "text.tex" }
    ]
},
```

Add your keybindings with the context key `latex_prefix_key.mode.your_mode`:

``` js
{
    "keys": ["b"], "command": "latex_prefix_key_insert_snippet", "args": { "contents": "\\textbf{$1}$0" },
    "context":
    [
        { "key": "selector", "operator": "equal", "operand": "text.tex" },
        { "key": "latex_prefix_key.mode.your_mode" }
    ]
},
```

### Available keybindings

If you are used to Auctex, then you feel familiar with the default keybindings. You can see the available keybindings and commands for any prefix keymap by pressing the prefix key (`;`) and `?`.

<!-- In addition a cheat sheet with the default keys is hosted [here](). -->
