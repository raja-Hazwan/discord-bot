import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
from discord import FFmpegPCMAudio
from yt_dlp import YoutubeDL




load_dotenv()
token = os.environ.get('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
music_queue = {}  # guild_id: list of (title, url)
is_playing = {}   # guild_id: bool
looping = {}  # guild_id: bool
def format_duration(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{str(seconds).zfill(2)}"



class MusicControlView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label="⏸ Pause", style=discord.ButtonStyle.red)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Paused.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)

    @discord.ui.button(label="▶️ Resume", style=discord.ButtonStyle.green)
    async def resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Resumed.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nothing is paused.", ephemeral=True)

    @discord.ui.button(label="⏭ Skip", style=discord.ButtonStyle.blurple)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Skipped.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)

    @discord.ui.button(label="🔁 Loop", style=discord.ButtonStyle.gray)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = self.ctx.guild.id
        current = looping.get(guild_id, False)
        looping[guild_id] = not current
        status = "enabled" if looping[guild_id] else "disabled"
        await interaction.response.send_message(f"🔁 Looping is now **{status}**.", ephemeral=True)


bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

@bot.event
async def on_member_join(member):
    await member.send(f'Welcome to the server, {member.name}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

@bot.command()
async def hallo(ctx):
    await ctx.send(f'Whats up ma nigga, {ctx.author.name}!')

@bot.command()
async def play(ctx, *, search: str):
    guild_id = ctx.guild.id

    if not ctx.author.voice:
        await ctx.send("❌ You need to be in a voice channel to play music.")
        return

    voice_channel = ctx.author.voice.channel

    # yt-dlp config
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'default_search': 'ytsearch',
        'noplaylist': True,
        'extract_flat': False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search, download=False)
        if 'entries' in info:
            info = info['entries'][0]  # from search result

    # Add full info object to queue
    if guild_id not in music_queue:
        music_queue[guild_id] = []
    music_queue[guild_id].append(info)

    await ctx.send(f"🎶 Added to queue: **{info.get('title', 'Unknown')}**")

    if not is_playing.get(guild_id):
        await start_playback(ctx, voice_channel)


async def start_playback(ctx, channel):
    guild_id = ctx.guild.id
    is_playing[guild_id] = True

    if ctx.voice_client is None:
        vc = await channel.connect()
    else:
        vc = ctx.voice_client
        if vc.channel != channel:
            await vc.move_to(channel)

    while music_queue[guild_id]:
        info = music_queue[guild_id][0]  # full yt-dlp info object
        title = info.get('title', 'Unknown')
        stream_url = info.get('url')
        duration_sec = info.get('duration', 0)
        duration_str = format_duration(duration_sec)
        thumbnail = info.get('thumbnail')

        # Create embed
        embed = discord.Embed(
            title="🎧 Now Playing",
            description=f"**{title}**",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Duration", value=duration_str, inline=True)
        if thumbnail:
            embed.set_image(url=thumbnail)

        view = MusicControlView(ctx)
        await ctx.send(embed=embed, view=view)

        done = asyncio.Event()

        def after_playing(error):
            if error:
                print(f"Playback error: {error}")
            bot.loop.call_soon_threadsafe(done.set)

        ffmpeg_opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        vc.play(FFmpegPCMAudio(stream_url, **ffmpeg_opts), after=after_playing)
        await done.wait()

        if not looping.get(guild_id, False):
            music_queue[guild_id].pop(0)

    is_playing[guild_id] = False
    await vc.disconnect()






@bot.command()
async def loop(ctx):
    guild_id = ctx.guild.id
    current = looping.get(guild_id, False)
    looping[guild_id] = not current
    if looping[guild_id]:
        await ctx.send("🔁 Looping is now **enabled**.")
    else:
        await ctx.send("🔁 Looping is now **disabled**.")


@bot.command()
async def pause(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("⏸️ Paused.")
    else:
        await ctx.send("❌ Nothing is playing.")

@bot.command()
async def resume(ctx):
    vc = ctx.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("▶️ Resumed.")
    else:
        await ctx.send("❌ Nothing is paused.")

@bot.command()
async def skip(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("⏭️ Skipped.")
    else:
        await ctx.send("❌ Nothing is playing.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected.")
    else:
        await ctx.send("I'm not in a voice channel.")

@bot.command()
async def queue(ctx):
    guild_id = ctx.guild.id
    if not music_queue.get(guild_id):
        await ctx.send("📭 Queue is empty.")
        return

    queue_list = [f"{i+1}. {title}" for i, (title, _) in enumerate(music_queue[guild_id])]
    await ctx.send("📜 **Current Queue:**\n" + "\n".join(queue_list))




bot.run(token, log_handler=handler, log_level=logging.DEBUG)