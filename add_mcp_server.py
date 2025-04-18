import sys
import json
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit, QMessageBox
)

CONFIG_FILE = Path("mcp_config.json")
DEFAULT_COMMAND = "./.venv/Scripts/python.exe"
AGENTS_DIR = Path("agents")

SAMPLE_SCRIPT = '''from mcp.server.fastmcp import FastMCP
from pydantic_ai import Agent

server = FastMCP("New Tool MCP Server")
agent = Agent("openai:gpt-4o", system_prompt="Be friendly and helpful.")

@server.tool()
async def sample_tool() -> str:
    return "This is a sample response from your tool."

if __name__ == "__main__":
    server.run()'''


class MCPServerEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCP Server Tool Manager")
        self.setGeometry(200, 200, 700, 600)

        self.server_list = QListWidget()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Server name (e.g. identity)")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Path to script (e.g. agents/identity_info_tool/identity.py)")
        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("Paste your tool server script here or click Generate Template...")

        add_button = QPushButton("Add Server")
        delete_button = QPushButton("Delete Selected Server")
        template_button = QPushButton("Generate Template Script")
        test_button = QPushButton("Test Selected Server Script")

        add_button.clicked.connect(self.add_server)
        delete_button.clicked.connect(self.delete_selected_server)
        template_button.clicked.connect(self.insert_sample_script)
        test_button.clicked.connect(self.test_selected_script)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Configured MCP Servers:"))
        layout.addWidget(self.server_list)
        layout.addWidget(QLabel("Add New MCP Server"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.path_input)
        layout.addWidget(QLabel("Paste Server Script:"))
        layout.addWidget(self.script_input)

        buttons = QHBoxLayout()
        buttons.addWidget(add_button)
        buttons.addWidget(delete_button)
        layout.addLayout(buttons)

        extras = QHBoxLayout()
        extras.addWidget(template_button)
        extras.addWidget(test_button)
        layout.addLayout(extras)

        self.setLayout(layout)
        self.load_servers()

    def load_servers(self):
        self.server_list.clear()
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.servers = data.get("mcpServers", {})
        else:
            self.servers = {}

        for name in self.servers:
            self.server_list.addItem(f"{name} -> {self.servers[name]['args'][-1]}")

    def add_server(self):
        name = self.name_input.text().strip()
        path = self.path_input.text().strip()
        script_code = self.script_input.toPlainText().strip()

        if not name or not path:
            QMessageBox.warning(self, "Missing Info", "Please enter both name and path.")
            return

        if not script_code:
            QMessageBox.warning(self, "Empty Script", "Script content is empty. Please paste or generate a script.")
            return

        if "server.run()" not in script_code or "@server.tool()" not in script_code:
            QMessageBox.warning(self, "Incomplete Script", "Script must contain @server.tool() and server.run().")
            return

        script_path = Path(path)
        full_path = Path.cwd() / script_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(script_code)

        self.servers[name] = {
            "command": DEFAULT_COMMAND,
            "args": [path]
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump({"mcpServers": self.servers}, f, indent=2)

        self.name_input.clear()
        self.path_input.clear()
        self.script_input.clear()
        self.load_servers()

    def delete_selected_server(self):
        selected = self.server_list.currentItem()
        if not selected:
            return

        name = selected.text().split(" -> ")[0]
        if name in self.servers:
            del self.servers[name]
            with open(CONFIG_FILE, "w") as f:
                json.dump({"mcpServers": self.servers}, f, indent=2)
            self.load_servers()

    def insert_sample_script(self):
        self.script_input.setPlainText(SAMPLE_SCRIPT)

    def test_selected_script(self):
        selected = self.server_list.currentItem()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a server to test.")
            return

        path = selected.text().split(" -> ")[-1]
        try:
            subprocess.run([DEFAULT_COMMAND, path], check=True)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Script Error", f"Error running script:\n{e}")
        except Exception as e:
            QMessageBox.warning(self, "Launch Failed", f"Could not run script: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MCPServerEditor()
    window.show()
    sys.exit(app.exec())