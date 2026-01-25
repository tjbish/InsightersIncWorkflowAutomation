# monday-client-writer

A simple Python CLI program that creates a new client item on a monday.com board and writes client info into columns using monday’s GraphQL API.

## What this does

When you run the script, it will:
1. Read `config.json` (API token, board ID, group ID, column IDs, defaults)
2. Create a new item (row) in your monday board (item name = client name)
3. Update columns like email, phone, company, and notes (optional)

---

## Requirements

- Python 3.9+ recommended
- A monday.com API token
- A board ID and group ID you want to write items into
- Column IDs for email/phone/company/notes on your board

---

## Setup

### 1 Install dependencies

```bash
pip install requests
