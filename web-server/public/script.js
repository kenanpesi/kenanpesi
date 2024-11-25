const socket = io('http://localhost:3000');
let selectedPC = null;

// DOM Elements
const pcList = document.getElementById('pc-list');
const terminal = document.getElementById('terminal');
const commandInput = document.getElementById('command-input');
const sendCommandBtn = document.getElementById('send-command');

// Update PC list
socket.on('pc-list-update', (pcs) => {
    pcList.innerHTML = '';
    pcs.forEach(pc => {
        const li = document.createElement('li');
        li.className = `list-group-item ${selectedPC === pc ? 'active' : ''}`;
        li.textContent = pc;
        li.onclick = () => {
            document.querySelectorAll('.list-group-item').forEach(item => {
                item.classList.remove('active');
            });
            li.classList.add('active');
            selectedPC = pc;
        };
        pcList.appendChild(li);
    });
});

// Handle command output
socket.on('command-output', (data) => {
    const output = document.createElement('pre');
    output.textContent = `${data.output}`;
    terminal.appendChild(output);
    terminal.scrollTop = terminal.scrollHeight;
});

// Send command
function sendCommand() {
    if (!selectedPC) {
        alert('Please select a PC first');
        return;
    }
    
    const command = commandInput.value.trim();
    if (!command) return;

    socket.emit('send-command', {
        pcName: selectedPC,
        command: command
    });

    const cmdLine = document.createElement('pre');
    cmdLine.textContent = `$ ${command}`;
    terminal.appendChild(cmdLine);
    
    commandInput.value = '';
    terminal.scrollTop = terminal.scrollHeight;
}

sendCommandBtn.onclick = sendCommand;
commandInput.onkeypress = (e) => {
    if (e.key === 'Enter') {
        sendCommand();
    }
};
