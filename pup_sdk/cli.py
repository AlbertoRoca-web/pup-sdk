"""Command line interface for Pup SDK."""

import asyncio
import sys
from typing import Optional

import click

from .client import PupClient
from .exceptions import PupError, PupConnectionError


@click.group()
@click.option("--base-url", default="http://localhost:8080", help="Alberto API base URL")
@click.option("--api-key", help="API key for authentication")
@click.option("--timeout", default=60, help="Request timeout in seconds")
@click.pass_context
def cli(ctx, base_url: str, api_key: Optional[str], timeout: int):
    """Pup SDK CLI - Talk to Alberto from your terminal!"""
    ctx.ensure_object(dict)
    ctx.obj["base_url"] = base_url
    ctx.obj["api_key"] = api_key
    ctx.obj["timeout"] = timeout


@cli.command()
@click.option("--message", "-m", help="Message to send to Alberto")
@click.option("--interactive", "-i", is_flag=True, help="Start interactive chat")
@click.pass_context
async def chat(ctx, message: Optional[str], interactive: bool):
    """Chat with Alberto."""
    
    client = PupClient(
        base_url=ctx.obj["base_url"],
        api_key=ctx.obj["api_key"],
        timeout=ctx.obj["timeout"],
    )
    
    try:
        await client.connect()
        
        if interactive:
            await _interactive_chat(client)
        elif message:
            response = await client.say_woof(message)
            print(f"Alberto: {response.response}")
            if response.reasoning:
                print(f"Reasoning: {response.reasoning}")
        else:
            print("Please provide a message with --message or use --interactive mode")
            
    except PupConnectionError as e:
        print(f"Connection error: {e}")
        sys.exit(1)
    except PupError as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        await client.close()


async def _interactive_chat(client: PupClient):
    """Run an interactive chat session."""
    print("Alberto Interactive Chat")
    print("Type 'quit', 'exit', or press Ctrl+C to stop\n")
    
    try:
        while True:
            try:
                message = input("You: ").strip()
                
                if message.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                    
                if not message:
                    continue
                    
                print("Alberto: ", end="", flush=True)
                response = await client.say_woof(message)
                print(response.response)
                
                if response.reasoning:
                    print(f"Reasoning: {response.reasoning}")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
                
    except Exception as e:
        print(f"Error during chat: {e}")


@cli.command()
@click.option("--directory", "-d", default=".", help="Directory to list")
@click.option("--recursive", "-r", is_flag=True, help="List recursively")
@click.pass_context
async def ls(ctx, directory: str, recursive: bool):
    """List files in a directory."""
    
    client = PupClient(
        base_url=ctx.obj["base_url"],
        api_key=ctx.obj["api_key"],
        timeout=ctx.obj["timeout"],
    )
    
    try:
        await client.connect()
        files = await client.list_files(directory=directory, recursive=recursive)
        
        if not files:
            print(f"No files found in {directory}")
            return
            
        print(f"Files in {directory}:")
        for file_info in files:
            icon = "DIR" if file_info.is_directory else "FILE"
            size = f"{file_info.size}B" if file_info.is_file else ""
            print(f"  {icon} {file_info.name.ljust(30)} {size}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        await client.close()


@cli.command()
@click.argument("file_path")
@click.option("--start-line", "-s", type=int, help="Start line number")
@click.option("--num-lines", "-n", type=int, help="Number of lines to read")
@click.pass_context
async def cat(ctx, file_path: str, start_line: Optional[int], num_lines: Optional[int]):
    """Read file contents."""
    
    client = PupClient(
        base_url=ctx.obj["base_url"],
        api_key=ctx.obj["api-key"],
        timeout=ctx.obj["timeout"],
    )
    
    try:
        await client.connect()
        content = await client.read_file(
            file_path=file_path,
            start_line=start_line,
            num_lines=num_lines,
        )
        
        print(f"Contents of {file_path}:")
        if content:
            lines = content.split('\n')
            start_num = start_line or 1
            for i, line in enumerate(lines, start=start_num):
                print(f"{i:4d} | {line}")
        else:
            print("(empty file)")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        await client.close()


@cli.command()
@click.argument("command")
@click.option("--cwd", help="Working directory")
@click.option("--timeout", default=60, help="Command timeout")
@click.pass_context
async def cmd(ctx, command: str, cwd: Optional[str], timeout: int):
    """Execute a shell command."""
    
    client = PupClient(
        base_url=ctx.obj["base_url"],
        api_key=ctx.obj["api_key"],
        timeout=ctx.obj["timeout"],
    )
    
    try:
        await client.connect()
        result = await client.run_command(
            command=command,
            working_directory=cwd,
            timeout=timeout,
        )
        
        print(f"Command: {result.command}")
        print(f"Exit code: {result.exit_code}")
        print(f"Execution time: {result.execution_time:.2f}s")
        
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        await client.close()


@cli.command()
@click.argument("search_query")
@click.option("--directory", "-d", default=".", help="Search directory")
@click.option("--max-results", default=20, help="Maximum results")
@click.pass_context
async def grep(ctx, search_query: str, directory: str, max_results: int):
    """Search for text in files."""
    
    client = PupClient(
        base_url=ctx.obj["base_url"],
        api_key=ctx.obj["api_key"],
        timeout=ctx.obj["timeout"],
    )
    
    try:
        await client.connect()
        results = await client.search_files(
            search_string=search_query,
            directory=directory,
            max_results=max_results,
        )
        
        if not results:
            print(f"No results found for '{search_query}' in {directory}")
            return
            
        print(f"Search results for '{search_query}':")
        for result in results:
            print(f"  File {result.file_path}:{result.line_number}")
            print(f"     {result.line_content.strip()}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        await client.close()


@cli.command()
@click.pass_context
async def status(ctx):
    """Check Alberto's status."""
    
    client = PupClient(
        base_url=ctx.obj["base_url"],
        api_key=ctx.obj["api_key"],
        timeout=ctx.obj["timeout"],
    )
    
    try:
        await client.connect()
        status = await client.get_status()
        
        print(f"Alberto Status:")
        print(f"  Available: {'Yes' if status.available else 'No'}")
        print(f"  Version: {status.version}")
        if status.current_directory:
            print(f"  Current dir: {status.current_directory}")
        if status.uptime:
            print(f"  Uptime: {status.uptime:.1f}s")
            
        print(f"  Capabilities:")
        for cap in status.capabilities:
            status_icon = "OK" if cap.enabled else "DISABLED"
            print(f"    {status_icon} {cap.name} - {cap.description}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        await client.close()


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=7860, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def web(host: str, port: int, reload: bool):
    """Launch the web interface."""
    print(f"Launching web interface on http://{host}:{port}")
    
    # Import here to avoid circular imports
    from .web import launch_web
    
    try:
        launch_web(host=host, port=port, reload=reload)
    except KeyboardInterrupt:
        print("\nWeb interface stopped")
    except Exception as e:
        print(f"Error launching web interface: {e}")
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    # Convert click command to handle async
    def _run_async(func):
        def wrapper(*args, **kwargs):
            return asyncio.run(func(*args, **kwargs))
        return wrapper
    
    # Patch async commands
    chat.callback = _run_async(chat.callback)
    ls.callback = _run_async(ls.callback)
    cat.callback = _run_async(cat.callback)
    cmd.callback = _run_async(cmd.callback)
    grep.callback = _run_async(grep.callback)
    status.callback = _run_async(status.callback)
    
    cli()


if __name__ == "__main__":
    main()