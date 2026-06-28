const API_URL = 'http://localhost:8000/api';

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadGoals();
    loadTransactions();
    loadSummary();
});

// ========== GOALS ==========
async function loadGoals() {
    const res = await fetch(`${API_URL}/goals/`);
    const goals = await res.json();
    const container = document.getElementById('goalList');
    container.innerHTML = goals.map(g => `
        <div class="goal-item">
            <div class="flex">
                <strong>${g.name}</strong>
                <span>$${g.current_amount} / $${g.target_amount}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${Math.min(g.progress, 100)}%"></div>
            </div>
            <div class="flex" style="font-size: 14px; color: #718096;">
                <span>${g.progress.toFixed(0)}% complete</span>
                <span>Due: ${new Date(g.deadline).toLocaleDateString()}</span>
            </div>
        </div>
    `).join('');
}

async function addGoal() {
    const name = document.getElementById('goalName').value;
    const target = parseFloat(document.getElementById('goalTarget').value);
    const deadline = document.getElementById('goalDeadline').value;
    
    if (!name || !target || !deadline) return alert('Please fill all fields');
    
    await fetch(`${API_URL}/goals/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, target_amount: target, deadline })
    });
    
    document.getElementById('goalName').value = '';
    document.getElementById('goalTarget').value = '';
    document.getElementById('goalDeadline').value = '';
    loadGoals();
    loadSummary();
}

// ========== TRANSACTIONS ==========
async function loadTransactions() {
    const res = await fetch(`${API_URL}/transactions/`);
    const txns = await res.json();
    const container = document.getElementById('txnList');
    container.innerHTML = txns.map(t => `
        <div class="txn-item flex">
            <span>${t.description}</span>
            <span style="color: ${t.amount >= 0 ? '#48bb78' : '#fc8181'}">
                ${t.amount >= 0 ? '+' : ''}$${t.amount}
            </span>
        </div>
    `).join('');
}

async function addTransaction() {
    const description = document.getElementById('txnDesc').value;
    const amount = parseFloat(document.getElementById('txnAmount').value);
    
    if (!description || !amount) return alert('Please fill all fields');
    
    await fetch(`${API_URL}/transactions/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description, amount })
    });
    
    document.getElementById('txnDesc').value = '';
    document.getElementById('txnAmount').value = '';
    loadTransactions();
    loadGoals();  // Refresh goals to update progress
    loadSummary();
}

// ========== SUMMARY ==========
async function loadSummary() {
    const res = await fetch(`${API_URL}/summary/`);
    const data = await res.json();
    document.getElementById('totalSaved').textContent = `$${data.total_saved.toFixed(2)}`;
    document.getElementById('goalCount').textContent = data.goals_count;
    document.getElementById('daysLeft').textContent = data.nearest_goal !== null ? `${data.nearest_goal} days` : 'No goals';
}
