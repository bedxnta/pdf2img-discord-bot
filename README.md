# 📄 Discord PDF Viewer Bot

A Discord bot that converts PDFs into images and lets you view them directly inside Discord with navigation controls.

---

## ✨ Features

* 📄 Detects PDFs when the bot is mentioned
* 🔁 Navigate pages with buttons (⬅️ ➡️)
* 🔢 Jump to any page using a modal
* 📚 "Show All" mode (grouped, no spam)
* 🔙 Revert back to page viewer
* 💬 Works with replies (mention + reply to PDF)
* 🧠 In-memory image handling (no file clutter)
* ⚡ Optional `all` keyword to instantly show all pages

---

## 🛠 Requirements

* Python 3.10+
* `discord.py`
* `pdf2image`
* `Pillow`
* Poppler (required for PDF conversion)

---

## 📦 Installation

### 1. Clone / Download

```bash
git clone https://github.com/bedxnta/pdf2img-discord-bot
cd pdf2img-discord-bot
```

---

### 2. Install Python dependencies

```bash
pip install discord.py pdf2image pillow
```

---

### 3. Install Poppler

#### 🐧 Linux (Ubuntu / Pop!_OS)

```bash
sudo apt install poppler-utils
```

#### 🪟 Windows

1. Download from:
   https://github.com/oschwartz10612/poppler-windows/releases/

2. Extract to:

```
C:\poppler
```

3. Add to PATH:

```
C:\poppler\Library\bin
```

OR set in code:

```python
convert_from_path(pdf_path, poppler_path=r"C:\poppler\Library\bin")
```

---

## 🔑 Setup

1. Go to Discord Developer Portal
2. Create a bot
3. Enable:

   * Message Content Intent
4. Copy bot token

Replace in code:

```python
TOKEN = "xyz"
```

⚠️ Never share your token publicly.

---

## ▶️ Run the Bot

```bash
python main.py
```

---

## 📌 Usage

### Basic

```
@BotName <attach PDF>
```

→ Opens interactive viewer

---

### Show All Immediately

```
@BotName all <attach PDF>
```

→ Sends all pages directly (grouped)

---

### Reply Mode

Reply to a message containing a PDF:

```
@BotName
```

---

### If no PDF found

```
No PDF detected.
```

---

## 🎮 Controls

| Button   | Action            |
| -------- | ----------------- |
| ⬅️       | Previous page     |
| ➡️       | Next page         |
| Jump     | Enter page number |
| Show All | Display all pages |
| Revert   | Return to viewer  |

---

## 🔧 Customization

### Change page limit

```python
convert_from_path(pdf_path, first_page=1, last_page=20)
```

---

### Adjust image quality

```python
page.save(buffer, format="JPEG", quality=70)
```

---

## 🧠 Notes

* Images are stored in memory (RAM), not on disk
* Temporary PDF file is deleted after processing
* Buttons only work for the original user

---

## 📜 License

Use it, modify it, break it, improve it — do whatever.

---

Built because I set up a study server.
