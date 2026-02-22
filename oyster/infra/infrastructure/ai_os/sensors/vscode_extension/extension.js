const vscode = require('vscode');


const HUB_CONFIG = 'aios.hubUrl';
const TOKEN_CONFIG = 'aios.token';


async function sendToHub(intent) {
  const config = vscode.workspace.getConfiguration();
  const hubUrl = config.get(HUB_CONFIG, 'http://127.0.0.1:8787/report');
  const token = config.get(TOKEN_CONFIG, '');


  // Get current file info
  const editor = vscode.window.activeTextEditor;
  let filePath = '';
  let fileExt = '';
  if (editor) {
    const doc = editor.document;
    filePath = doc.uri.fsPath;
    fileExt = doc.languageId;
  }


  // Get workspace folder
  let workspaceFolder = '';
  if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
    workspaceFolder = vscode.workspace.workspaceFolders[0].uri.fsPath;
  }


  const payload = {
    source: 'vscode',
    domain: workspaceFolder || 'unknown',
    title: filePath || 'no-file',
    intent: intent,
    meta: {
      file_ext: fileExt,
      workspace: workspaceFolder
    }
  };


  try {
    const res = await fetch(hubUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-AIOS-Token': token
      },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      vscode.window.setStatusBarMessage(`AI OS: Intent set to ${intent}`, 3000);
    } else {
      vscode.window.showWarningMessage(`AI OS: Failed to send (${res.status})`);
    }
  } catch (e) {
    vscode.window.showWarningMessage(`AI OS: Cannot connect to hub`);
  }
}


function activate(context) {
  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('aios.setIntentBD', () => sendToHub('bd')),
    vscode.commands.registerCommand('aios.setIntentResearch', () => sendToHub('research')),
    vscode.commands.registerCommand('aios.setIntentContent', () => sendToHub('content')),
    vscode.commands.registerCommand('aios.setIntentInfra', () => sendToHub('infra')),
    vscode.commands.registerCommand('aios.setIntentNone', () => sendToHub('none'))
  );
}


function deactivate() {}


module.exports = { activate, deactivate };
