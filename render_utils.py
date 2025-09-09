import asyncio

async_output = {}
async_output_lock = asyncio.Lock()

async def flush_async_output(task_id: str):
    async with async_output_lock:
        if task_id not in async_output:
            raise ValueError(f"No async output for task: {task_id}")
        else:
            data = async_output[task_id]
            del async_output[task_id]
    await render_model_output(f"** 🤖✏️ Output for async task: {task_id}\n\n")
    await render_model_output(data)


async def render_model_output(data: str,
                        log: bool = True,
                        async_task: bool = False,
                        task_id: str | None = None):
    async with async_output_lock:
        if async_task and task_id:
            if task_id in async_output:
                async_output[task_id] += data
                data = ''
            else:
                async_output[task_id] = data
                data = "** 🤖✏️ Gathering output from async task ... please hold\n"
    if data:
        if log:
            with open('logs/render_stdout.log', 'a') as f:
                f.write(data)
        print(data, end="", flush=True)
