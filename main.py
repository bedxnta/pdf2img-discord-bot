import discord
import os
from pdf2image import convert_from_path
from io import BytesIO

TOKEN = "xyz"

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)


class JumpModal(discord.ui.Modal, title="Jump to Page"):
    page_number = discord.ui.TextInput(label="Enter page number")

    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer

    async def on_submit(self, interaction: discord.Interaction):
        try:
            page = int(self.page_number.value)
            if 1 <= page <= len(self.viewer.images):
                self.viewer.index = page - 1
                await self.viewer.send_single(interaction)
            else:
                await interaction.response.send_message(
                    "Invalid page number.", ephemeral=True
                )
        except:
            await interaction.response.send_message(
                "Enter a valid number.", ephemeral=True
            )


class PDFViewer(discord.ui.View):
    def __init__(self, images, author_id):
        super().__init__(timeout=300)
        self.images = images
        self.author_id = author_id
        self.index = 0
        self.message = None
        self.show_all_messages = []

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.author_id

    def get_file(self, index):
        self.images[index].seek(0)
        return discord.File(self.images[index], filename=f"page_{index+1}.jpg")

    async def send_single(self, interaction):
        file = self.get_file(self.index)
        await interaction.response.edit_message(
            content=f"Page {self.index + 1}/{len(self.images)}",
            attachments=[file],
            view=self
        )

    async def recreate_single(self, channel):
        msg = await channel.send(
            content=f"Page {self.index + 1}/{len(self.images)}",
            file=self.get_file(self.index),
            view=self
        )
        self.message = msg

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button):
        if self.index > 0:
            self.index -= 1
        await self.send_single(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button):
        if self.index < len(self.images) - 1:
            self.index += 1
        await self.send_single(interaction)

    @discord.ui.button(label="Jump", style=discord.ButtonStyle.success)
    async def jump(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(JumpModal(self))

    @discord.ui.button(label="Show All", style=discord.ButtonStyle.primary)
    async def show_all(self, interaction: discord.Interaction, button):

        await interaction.response.defer()

        # Delete the viewer message
        await interaction.message.delete()

        self.show_all_messages = []

        batch = []
        for i in range(len(self.images)):
            batch.append(self.get_file(i))

            # Send when batch reaches 10
            if len(batch) == 10:
                msg = await interaction.channel.send(files=batch)
                self.show_all_messages.append(msg)
                batch = []

        # Send remaining pages
        if batch:
            msg = await interaction.channel.send(files=batch)
            self.show_all_messages.append(msg)

        # Send revert control
        revert_msg = await interaction.channel.send(
            content="Showing all pages.",
            view=RevertView(self)
        )

        self.show_all_messages.append(revert_msg)

    async def revert_to_single(self, interaction):

        # Delete all show-all messages
        for msg in self.show_all_messages:
            try:
                await msg.delete()
            except:
                pass

        self.show_all_messages = []

        # Recreate original viewer
        await self.recreate_single(interaction.channel)


class RevertView(discord.ui.View):
    def __init__(self, viewer):
        super().__init__(timeout=300)
        self.viewer = viewer

    @discord.ui.button(label="Revert", style=discord.ButtonStyle.danger)
    async def revert(self, interaction: discord.Interaction, button):
        await interaction.response.defer()
        await self.viewer.revert_to_single(interaction)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user not in message.mentions:
        return

    pdf_attachment = None

    for attachment in message.attachments:
        if attachment.filename.lower().endswith(".pdf"):
            pdf_attachment = attachment
            break

    if not pdf_attachment and message.reference:
        try:
            replied = await message.channel.fetch_message(
                message.reference.message_id
            )
            for attachment in replied.attachments:
                if attachment.filename.lower().endswith(".pdf"):
                    pdf_attachment = attachment
                    break
        except:
            pass

    if not pdf_attachment:
        await message.channel.send("No PDF detected.")
        return

    status = await message.channel.send("Converting PDF...")

    pdf_path = f"temp_{message.id}.pdf"
    await pdf_attachment.save(pdf_path)

    try:
        pages = convert_from_path(pdf_path, first_page=1, last_page=20)

        image_buffers = []

        for page in pages:
            buffer = BytesIO()
            page.save(buffer, format="JPEG", quality=70)
            buffer.seek(0)
            image_buffers.append(buffer)

        await status.delete()

        viewer = PDFViewer(image_buffers, message.author.id)

                # Detect if user wants all pages directly
        show_all_requested = "all" in message.content.lower()

        viewer = PDFViewer(image_buffers, message.author.id)

        if show_all_requested:
            # Send a temporary message to trigger show_all logic
            temp_msg = await message.channel.send("Processing all pages...")

            # Fake interaction object is not possible, so directly call logic
            batch = []
            viewer.show_all_messages = []

            for i in range(len(image_buffers)):
                batch.append(viewer.get_file(i))

                if len(batch) == 10:
                    msg = await message.channel.send(files=batch)
                    viewer.show_all_messages.append(msg)
                    batch = []

            if batch:
                msg = await message.channel.send(files=batch)
                viewer.show_all_messages.append(msg)

            revert_msg = await message.channel.send(
                content="Showing all pages.",
                view=RevertView(viewer)
            )

            viewer.show_all_messages.append(revert_msg)

            await temp_msg.delete()

        else:
            msg = await message.channel.send(
                content=f"Page 1/{len(image_buffers)}",
                file=viewer.get_file(0),
                view=viewer
            )

            viewer.message = msg

    except Exception as e:
        await status.delete()
        await message.channel.send(f"Error: {e}")

    finally:
        os.remove(pdf_path)


bot.run(TOKEN)