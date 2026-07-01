#!/usr/bin/env python3
import sys
import os
import json
import socket
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, Gdk, Gio, WebKit, GLib

BROKER_SOCKET = "/run/cerynix/broker.sock"

class CerynixApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.cerynixos.UI", flags=Gio.ApplicationFlags.FLAGS_NONE)
        
    def do_activate(self):
        self.win = Gtk.ApplicationWindow(application=self)
        self.win.set_title("CerynixAI")
        self.win.set_default_size(400, 800)
        
        # Remove decorations for the pure glassmorphism sliding panel look
        self.win.set_decorated(False)
        
        # In a real environment, position this on the right edge of the screen
        # Since GTK4 removes direct window positioning for Wayland compatibility,
        # GNOME Shell handles the placement via the extension.
        
        # WebKit Setup
        web_context = WebKit.WebContext.get_default()
        web_context.set_sandbox_enabled(True) # Extreme security
        
        self.webview = WebKit.WebView()
        self.webview.set_background_color(Gdk.RGBA(0, 0, 0, 0)) # Transparent background
        
        # Bridge JS to Python natively via UDS
        user_content = self.webview.get_user_content_manager()
        user_content.register_script_message_handler("cerynix_bridge")
        user_content.connect("script-message-received::cerynix_bridge", self.on_js_message)
        
        # Inject the JS bridge into the HTML environment
        bridge_script = WebKit.UserScript(
            source="""
            window.sendToBroker = function(command, args) {
                window.webkit.messageHandlers.cerynix_bridge.postMessage(JSON.stringify({command: command, args: args}));
            };
            """,
            injected_frames=WebKit.UserContentInjectedFrames.ALL_FRAMES,
            injection_time=WebKit.UserScriptInjectionTime.START
        )
        user_content.add_script(bridge_script)
        
        self.win.set_child(self.webview)
        
        # Load local HTML file directly (Zero open network ports)
        ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../public/index.html"))
        self.webview.load_uri(f"file://{ui_path}")
        
        self.win.present()
        
    def on_js_message(self, user_content_manager, javascript_result):
        # Native IPC via UDS to the Action Broker
        payload = javascript_result.get_js_value().to_string()
        print(f"Received from UI: {payload}")
        
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.connect(BROKER_SOCKET)
                s.sendall(payload.encode('utf-8'))
                response = s.recv(4096).decode('utf-8')
                
            # Send response back to JS
            safe_resp = json.dumps(response)
            self.webview.evaluate_javascript(f"window.receiveFromBroker({safe_resp})")
        except Exception as e:
            error_msg = json.dumps({"error": str(e)})
            self.webview.evaluate_javascript(f"window.receiveFromBroker({error_msg})")

if __name__ == "__main__":
    app = CerynixApp()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
