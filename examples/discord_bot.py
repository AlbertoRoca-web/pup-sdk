"""Discord bot integration example for Pup SDK."""

import asyncio
import discord
from discord.ext import commands
import sys
sys.path.append('..')

from pup_sdk import PupClient
from pup_sdk.exceptions import PupConnectionError, PupError

# Bot configuration
BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"  # Replace with your actual token
ALBERTO_URL = "http://localhost:8080"

# Discord bot intents
intents = discord.Intents.default()
intents.message_content = True

# Bot instance
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    description="🐕 Alberto the Code Puppy - Your Discord coding assistant!"
)

# Global Alberto client
alberto_client: PupClient = None


@bot.event
async def on_ready():
    """Called when bot is ready."""
    global alberto_client
    
    # Connect to Alberto
    try:
        alberto_client = await PupClient.connect(base_url=ALBERTO_URL)
        print(f"🐕 Connected to Alberto as {bot.user}")
        print(f"📱 Connected to {len(bot.guilds)} servers")
        
        # Set bot status
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="🐕 Helping developers code!"
            )
        )
        
    except PupConnectionError:
        print("⚠️ Could not connect to Alberto - running in demo mode")
    except Exception as e:
        print(f"❌ Error: {e}")


@bot.event
async def on_guild_join(guild):
    """Called when bot joins a new server."""
    print(f"🎉 Joined new server: {guild.name}")
    
    # Send welcome message to general channel
    general_channel = None
    for channel in guild.text_channels:
        if channel.name.lower() in ['general', 'chat', 'welcome']:
            general_channel = channel
            break
    
    if general_channel:
        embed = discord.Embed(
            title="🐕 Alberto the Code Puppy is here!",
            description=(
                "Woof! I'm Alberto, your friendly coding assistant! 🐶\n\n"
                "**What I can do:**\n"
                "• `!ask <question>` - Ask me anything about coding\n"
                "• `!run <command>` - Execute shell commands\n"
                "• `!list [path]` - List files and directories\n"
                "• `!read <file>` - Read file contents\n"
                "• `!search <query>` - Search code in files\n"
                "• `!status` - Check my status\n\n"
                "Try `!ask What can you help me with?` to get started!"
            ),
            color=discord.Color.purple()
        )
        embed.set_footer(text="Made with 🐶 love by Alberto")
        await general_channel.send(embed=embed)


@bot.command(name='ask', help='Ask Alberto a question about coding')
async def ask(ctx, *, question: str):
    """Ask Alberto a question."""
    if not question:
        await ctx.send("You need to ask me something! Try `!ask What can you help me with?`")
        return
        
    await ctx.typing()  # Show typing indicator
    
    try:
        if alberto_client:
            response = await alberto_client.say_woof(question)
            
            # Create nice embed
            embed = discord.Embed(
                title="🤔 Question",
                description=question,
                color=discord.Color.blue()
            )
            embed.add_field(name="🐕 Alberto's Response", value=response.response[:1024], inline=False)
            
            if len(response.response) > 1024:
                embed.add_field(
                    name="📄 Continued",
                    value=response.response[1024:2048],
                    inline=False
                )
            
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                "🐕 Woof! Alberto is offline right now, but I'd love to help you with your coding questions "
                "when he's back. Try again later! 🐾"
            )
            
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")


@bot.command(name='run', help='Run a shell command')
async def run_command(ctx, *, command: str):
    """Run a shell command."""
    if not command:
        await ctx.send("You need to provide a command! Try `!run echo 'hello'`")
        return
        
    await ctx.typing()
    
    try:
        if alberto_client:
            result = await alberto_client.run_command(command)
            
            embed = discord.Embed(
                title="💻 Shell Command",
                description=f"`{command}`",
                color=discord.Color.green() if result.success else discord.Color.red()
            )
            
            embed.add_field(name="Exit Code", value=str(result.exit_code or "N/A"))
            embed.add_field(name="Execution Time", value=f"{result.execution_time:.2f}s")
            
            if result.stdout:
                embed.add_field(
                    name="📤 STDOUT",
                    value=f"```\n{result.stdout[:1000]}\n```",
                    inline=False
                )
            
            if result.stderr:
                embed.add_field(
                    name="📥 STDERR",
                    value=f"```\n{result.stderr[:1000]}\n```",
                    inline=False
                )
            
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("🐕 Shell commands are not available when Alberto is offline!")
            
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")


@bot.command(name='list', help='List files in a directory')
async def list_files(ctx, path: str = "."):
    """List files in a directory."""
    await ctx.typing()
    
    try:
        if alberto_client:
            files = await alberto_client.list_files(path, recursive=False)
            
            if not files:
                await ctx.send(f"No files found in `{path}`")
                return
                
            embed = discord.Embed(
                title=f"📁 Files in `{path}`",
                color=discord.Color.blue()
            )
            
            # Format file list
            file_list = []
            for file_info in files[:20]:  # Limit to 20 files
                icon = "📁" if file_info.is_directory else "📄"
                size = f" ({file_info.size}B)" if file_info.is_file else ""
                file_list.append(f"{icon} {file_info.name}{size}")
            
            embed.description = "\n".join(file_list)
            
            if len(files) > 20:
                embed.set_footer(text=f"Showing 20 of {len(files)} items")
            
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("🐕 File operations are not available when Alberto is offline!")
            
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")


@bot.command(name='read', help='Read the contents of a file')
async def read_file(ctx, file_path: str):
    """Read file contents."""
    if not file_path:
        await ctx.send("You need to provide a file path! Try `!read README.md`")
        return
        
    await ctx.typing()
    
    try:
        if alberto_client:
            content = await alberto_client.read_file(file_path)
            
            embed = discord.Embed(
                title=f"📄 Contents of `{file_path}`",
                color=discord.Color.blue()
            )
            
            # Split content if it's too long
            if len(content) > 2000:
                embed.description = f"File is {len(content)} characters. Showing first 2000:\n\n```\n{content[:2000]}\n```"
            else:
                embed.description = f"```\n{content}\n```"
            
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("🐕 File reading is not available when Alberto is offline!")
            
    except Exception as e:
        await ctx.send(f"❌ Error reading file: {str(e)}")


@bot.command(name='search', help='Search for text in files')
async def search_files(ctx, *, query: str):
    """Search for text in files."""
    if not query:
        await ctx.send("You need to provide a search query! Try `!search async def`")
        return
        
    await ctx.typing()
    
    try:
        if alberto_client:
            results = await alberto_client.search_files(query, max_results=15)
            
            if not results:
                await ctx.send(f"No results found for `{query}`")
                return
                
            embed = discord.Embed(
                title=f"🔍 Search results for `{query}`",
                color=discord.Color.orange()
            )
            
            for result in results[:10]:
                filename = result.file_path.split('/')[-1]
                line_preview = result.line_content.strip()[:100]
                embed.add_field(
                    name=f"📄 {filename}:{result.line_number}",
                    value=line_preview,
                    inline=False
                )
            
            embed.set_footer(text=f"Found {len(results)} results | Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("🐕 Search is not available when Alberto is offline!")
            
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")


@bot.command(name='status', help='Check Alberto\'s status')
async def status(ctx):
    """Check Alberto's status."""
    try:
        if alberto_client:
            status_info = await alberto_client.get_status()
            
            embed = discord.Embed(
                title="🐕 Alberto's Status",
                color=discord.Color.green() if status_info.available else discord.Color.red()
            )
            
            embed.add_field(name="📝 Version", value=status_info.version)
            embed.add_field(name="🟢 Available", value="Yes" if status_info.available else "No")
            
            if status_info.current_directory:
                embed.add_field(name="📁 Current Directory", value=f"`{status_info.current_directory}`")
            
            if status_info.uptime:
                embed.add_field(name="⏱️ Uptime", value=f"{status_info.uptime:.1f}s")
            
            # Add capabilities
            capabilities = [cap.name for cap in status_info.capabilities if cap.enabled]
            embed.add_field(
                name="🛠️ Capabilities",
                value=", ".join(capabilities),
                inline=False
            )
            
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("🐕 Alberto is currently offline or in demo mode!")
            
    except Exception as e:
        await ctx.send(f"❌ Error checking status: {str(e)}")


@bot.command(name='help_alberto', help='Show Alberto bot help')
async def help_alberto(ctx):
    """Show help for Alberto commands."""
    embed = discord.Embed(
        title="🐕 Alberto Commands",
        description="All the commands you can use with Alberto the Code Puppy!",
        color=discord.Color.purple()
    )
    
    commands = [
        ("!ask <question>", "Ask Alberto anything about coding"),
        ("!run <command>", "Execute a shell command"),
        ("!list [path]", "List files in a directory"),
        ("!read <file>", "Read the contents of a file"),
        ("!search <query>", "Search for text in files"),
        ("!status", "Check Alberto's current status"),
    ]
    
    for command, description in commands:
        embed.add_field(name=command, value=description, inline=False)
    
    embed.add_field(
        name="💡 Tips",
        value=(
            "• Alberto can help with Python, JavaScript, web dev, and more!\n"
            "• Use code blocks ```` ```` for better formatting\n"
            "• Alberto is powered by code-puppy AI assistance"
        ),
        inline=False
    )
    
    embed.set_footer(text="Made with 🐶 love by Alberto")
    await ctx.send(embed=embed)


async def main():
    """Start the Discord bot."""
    print("🐕 Starting Alberto Discord Bot...")
    
    if BOT_TOKEN == "YOUR_DISCORD_BOT_TOKEN":
        print("❌ Please set your Discord bot token in the BOT_TOKEN variable")
        return
    
    try:
        await bot.start(BOT_TOKEN)
    except discord.errors.LoginFailure:
        print("❌ Invalid Discord token. Please check your BOT_TOKEN.")
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if alberto_client:
            await alberto_client.close()


if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())