import re
import threading
import gradio as gr
from gui.haku_character import haku_character
from tag_list import generate_tag_files
from typing import Optional
from queue import Queue
from datetime import datetime

task_queue = Queue()
results = {}
completed_tasks = []
current_task = None
queue_lock = threading.Lock()


def generate_task_id(task_type, params):
    timestamp = datetime.now().strftime("%m%d%H%M%S")

    if task_type == "haku":
        names = params.get("names", "")
        if names:
            first_tag = names.split(",")[0].strip()
            first_tag = re.sub(r"[^a-zA-Z0-9]", "", first_tag)
            first_tag = first_tag[:10] if len(first_tag) > 10 else first_tag
            return f"haku_{timestamp}_{first_tag}"
        else:
            return f"haku_{timestamp}_notags"
    elif task_type == "tag":
        return f"tag_{timestamp}"
    else:
        return f"unknown_{timestamp}"


def process_haku_task(task_id, params):
    try:
        names = params["names"]
        required = params["required"]
        exclude = params["exclude"]
        max_images = params["max_images"]
        ratings = params["ratings"]
        score = params["score"]
        db_path = params["db_path"]
        image_path = params["image_path"]
        output_path = params["output_path"]
        id_range_min = params["id_range_min"]
        id_range_max = params["id_range_max"]
        add_character_category_path = params["add_character_category_path"]
        export_images = params["export_images"]
        process_threads = params["process_threads"]
        id_input = params["id_input"]
        id_file = params["id_file"]
        # Input validation
        names_list = [n.strip() for n in names.split(",") if n.strip()] if names else []
        required_list = (
            [r.strip() for r in required.split(",") if r.strip()] if required else []
        )
        exclude_list = (
            [e.strip() for e in exclude.split(",") if e.strip()] if exclude else []
        )

        # Convert numerical inputs
        max_posts = max_images if max_images >= 0 else -1
        score_value = score if score >= 0 else -1
        id_min = id_range_min
        id_max = id_range_max

        # Convert ratings
        rating_list = []
        for r in ratings.split(","):
            rating = _safe_int(r.strip(), default=None)
            if rating is None or rating not in {0, 1, 2, 3}:
                raise ValueError(f"Invalid rating value: {r}")
            rating_list.append(rating)

        # Convert ID inputs
        id_list = []
        error_msgs = []

        if id_input:
            invalid_lines = []
            for idx, line in enumerate(id_input.splitlines(), start=1):
                stripped = line.strip()
                if not stripped:
                    continue

                try:
                    # Allow for other characters before and after but with significant digits,such as "ID: 123"
                    number = int("".join(filter(str.isdigit, stripped)))
                    id_list.append(number)
                except ValueError:
                    invalid_lines.append(f"The {idx} line: {stripped}")

            if invalid_lines:
                error_msgs.append(
                    "The following line contains an invalid ID format:"
                    + "\n".join(invalid_lines)
                )

        if id_file:
            try:
                with open(id_file, "r") as f:
                    file_ids = []
                    for line_num, line in enumerate(f, start=1):
                        stripped = line.strip()
                        if not stripped:
                            continue
                        try:
                            file_ids.append(int(stripped))
                        except ValueError:
                            error_msgs.append(
                                f"File's {line_num} line is invalid: {stripped}"
                            )
                    id_list.extend(file_ids)
            except Exception as e:
                error_msgs.append(f"File load failed: {str(e)}")

        unique_ids = list(set(id_list))
        if len(unique_ids) != len(id_list):
            error_msgs.append(
                f"Find duplicate ID, removed duplicates (remaining {len(unique_ids)})"
            )

        if error_msgs:
            return "\n".join(error_msgs)

        result = haku_character(
            names=names_list,
            required=required_list,
            exclude=exclude_list,
            max_posts=max_posts,
            ratings=rating_list,
            score_threshold=score_value,
            db_path=db_path,
            image_path=image_path,
            output_path=output_path,
            id_range_min=id_min,
            id_range_max=id_max,
            add_character_category_path=add_character_category_path,
            export_images=export_images,
            process_threads=process_threads,
            id_list=unique_ids,
            export_id_file=id_file,
        )

        return result
    except Exception as e:
        return f"Error occurred: {str(e)}"


def process_tag_task(task_id, params):
    try:
        db_path = params["db_path"]
        output_dir = params["output_dir"]

        result = generate_tag_files(db_path, output_dir)
        return result
    except Exception as e:
        return f"Error occurred: {str(e)}"


def worker():
    global current_task

    while True:
        task_data = task_queue.get()
        if task_data is None:
            break

        task_id, task_type, params = task_data

        with queue_lock:
            current_task = task_id

        if task_type == "haku":
            result = process_haku_task(task_id, params)
        elif task_type == "tag":
            result = process_tag_task(task_id, params)
        else:
            result = f"Error occurred: {task_type}"

        with queue_lock:
            results[task_id] = result
            completed_tasks.append(task_id)
            current_task = None

        task_queue.task_done()


worker_thread = threading.Thread(target=worker, daemon=True)
worker_thread.start()


def submit_haku_task(
    names,
    required,
    exclude,
    max_images,
    ratings,
    score,
    db_path,
    image_path,
    output_path,
    id_range_min,
    id_range_max,
    add_character_category_path,
    export_images,
    process_threads,
    id_input,
    id_file,
):
    task_id = generate_task_id("haku", params)

    params = {
        "names": names,
        "required": required,
        "exclude": exclude,
        "max_images": max_images,
        "ratings": ratings,
        "score": score,
        "db_path": db_path,
        "image_path": image_path,
        "output_path": output_path,
        "id_range_min": id_range_min,
        "id_range_max": id_range_max,
        "add_character_category_path": add_character_category_path,
        "export_images": export_images,
        "process_threads": process_threads,
        "id_input": id_input,
        "id_file": id_file,
    }

    task_queue.put((task_id, "haku", params))

    return f"Task submitted (ID: {task_id}), current queue length: {task_queue.qsize()}"


def submit_tag_task(db_path, output_dir):
    task_id = generate_task_id("tag", params)

    params = {
        "db_path": db_path,
        "output_dir": output_dir,
    }

    task_queue.put((task_id, "tag", params))

    return f"Task submitted (ID: {task_id}), current queue length: {task_queue.qsize()}"


def get_queue_status():
    with queue_lock:
        queue_size = task_queue.qsize()
        current = current_task
        completed = completed_tasks.copy()
        results_copy = results.copy()

    status = f"Current queue length: {queue_size}\n\n"

    if current:
        status += f"The task currently being processed: {current}\n\n"

    if completed:
        status += "Completed tasks:\n"
        for task_id in completed:
            result = results_copy.get(task_id, "Not found")
            status += (
                f"- {task_id}: {result[:100]}{'...' if len(result) > 100 else ''}\n"
            )
    else:
        status += "No completed tasks\n"

    return status


def _safe_int(value: str, default: Optional[int] = None) -> int:
    """Safely convert string to integer."""
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return default if default is not None else 0


with gr.Blocks(title="HakuBooru GUI") as blocks:
    gr.Markdown("# HakuBooru GUI")

    with gr.Row():
        with gr.Column(scale=2):
            with gr.Accordion("Basic Settings", open=True):
                with gr.Row():
                    with gr.Column(min_width=300):
                        names = gr.Textbox(
                            lines=3,
                            label="Tags (comma-separated)",
                            placeholder="Enter tags like: kamisato_ayaka, seele_vollerei",
                        )
                        required = gr.Textbox(
                            label="Required Tags", placeholder="solo, highres"
                        )
                        exclude = gr.Textbox(
                            label="Excluded Tags", placeholder="lowres, nsfw"
                        )

                    with gr.Column():
                        max_images = gr.Number(
                            value=-1, label="Max Images (-1 for no limit)", precision=0
                        )
                        ratings = gr.Textbox(
                            value="0,1,2,3", label="Allowed Ratings (0-3)"
                        )
                        score = gr.Number(
                            value=-1, label="Minimum Score (-1 for auto)", precision=0
                        )

            with gr.Accordion("Advanced Settings", open=True):
                with gr.Row():
                    db_path = gr.Textbox(
                        value="./data/danbooru2023.db", label="Database Path"
                    )
                    image_path = gr.Textbox(
                        value="./images/images", label="Image Archive Path"
                    )
                    output_path = gr.Textbox(value="./out", label="Output Directory")

                with gr.Row():
                    id_range_min = gr.Number(
                        value=0, label="Minimum Post ID", precision=0
                    )
                    id_range_max = gr.Number(
                        value=10_000_000, label="Maximum Post ID", precision=0
                    )
                    add_character_category_path = gr.Checkbox(
                        value=True, label="Organize by Tags"
                    )
                    export_images = gr.Checkbox(value=True, label="Enable Export")
                    process_threads = gr.Number(
                        value=4, label="Processing Threads", precision=0
                    )

            with gr.Accordion("Tag List", open=False):
                with gr.Row():
                    tag_db_path = gr.Textbox(
                        value="./data/danbooru2023.db", label="Database Path"
                    )
                    tag_output_dir = gr.Textbox(
                        value="./out/tag_list", label="Output Directory"
                    )
                gen_tags_btn = gr.Button("Export Tag List", variant="secondary")

            with gr.Accordion("ID List", open=False):
                gr.Markdown(
                    "When the `ID list` is not None, all conditions in the `Basic Settings` will be ignored."
                )
                with gr.Row():
                    id_input = gr.Textbox(
                        label="List of ID inputs",
                        placeholder="Example:\n12345\n67890\n13579",
                        lines=3,
                    )
                    id_file = gr.File(
                        label="Or upload ID list file",
                        file_types=[".txt"],
                        type="filepath",
                    )

            run_button = gr.Button("Start Processing", variant="primary")
            submit_output = gr.Textbox(label="Commit queue", interactive=False)

        with gr.Column(scale=1):
            gr.Markdown("## Task queue status")
            refresh_btn = gr.Button("Refresh status")
            queue_status = gr.Textbox(
                label="Queue status", interactive=False, lines=20, value="No task"
            )

    run_button.click(
        submit_haku_task,
        inputs=[
            names,
            required,
            exclude,
            max_images,
            ratings,
            score,
            db_path,
            image_path,
            output_path,
            id_range_min,
            id_range_max,
            add_character_category_path,
            export_images,
            process_threads,
            id_input,
            id_file,
        ],
        outputs=submit_output,
    )

    gen_tags_btn.click(
        submit_tag_task,
        inputs=[tag_db_path, tag_output_dir],
        outputs=submit_output,
    )

    refresh_btn.click(get_queue_status, inputs=None, outputs=queue_status)

    blocks.load(get_queue_status, inputs=None, outputs=queue_status)

blocks.launch(server_port=2104, inbrowser=True, show_error=True)
