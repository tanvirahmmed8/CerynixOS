import St from 'gi://St';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';

let cerynixAppProcess = null;

export default class CerynixExtension extends Extension {
    enable() {
        // Create the panel button
        this._indicator = new PanelMenu.Button(0.0, 'CerynixAI', false);
        
        // Add the sparkle icon ✨
        let icon = new St.Label({
            text: '✨',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'cerynix-panel-icon'
        });
        
        this._indicator.add_child(icon);
        
        // Toggle the GTK app on click
        this._indicator.connect('button-press-event', () => {
            if (cerynixAppProcess) {
                // In a production environment, we'd use DBus to toggle visibility.
                // For now, we terminate the process to hide it.
                GLib.spawn_command_line_async('killall cerynix_app.py');
                cerynixAppProcess = null;
            } else {
                // Spawn the GTK4 Python app
                // It renders on the right side of the screen
                GLib.spawn_command_line_async('/run/current-system/sw/bin/python3 /etc/nixos/modules/desktop/src/cerynix_app.py');
                cerynixAppProcess = true; // Simplified tracking
            }
        });
        
        // Add to the top right system bar (Status Area)
        Main.panel.addToStatusArea('cerynix-ai', this._indicator, 1, 'right');
    }

    disable() {
        if (this._indicator) {
            this._indicator.destroy();
            this._indicator = null;
        }
        if (cerynixAppProcess) {
            GLib.spawn_command_line_async('killall cerynix_app.py');
            cerynixAppProcess = null;
        }
    }
}
