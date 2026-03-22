default:
    @just --list

install:
    ln -sf "{{justfile_directory()}}/ticket" ~/.local/bin/tk
    @for plugin in {{justfile_directory()}}/plugins/ticket-*; do \
        ln -sf "$plugin" ~/.local/bin/$(basename "$plugin"); \
    done
    @echo "Installed tk + plugins to ~/.local/bin"

test:
	uv run --with behave behave
