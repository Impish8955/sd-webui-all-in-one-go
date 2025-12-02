import modules.scripts as scripts
import gradio as gr
from modules import processing, sd_models, sd_samplers
import copy
import random

class Script(scripts.Script):
    def title(self):
        return "All in one go"

    def show(self, is_img2img):
        return scripts.AlwaysVisible if False else True

    def ui(self, is_img2img):
        self.PREV_OPTION = "From previous generation"
        self.MAX_ROWS = 20
        
        checkpoints_list = sd_models.checkpoint_tiles()
        samplers_list = [s.name for s in sd_samplers.all_samplers]
        schedulers_list = ["Automatic", "Uniform", "Karras", "Exponential", "Polyexponential", "SGM Uniform"]
        
        options = [self.PREV_OPTION]
        
        rows_refs = []
        all_inputs = []

        with gr.Accordion("All in one go Settings", open=True):
            
           
            gr.Markdown(
                """
                <div style="padding: 12px; border: 1px solid #bdc3c7; border-radius: 8px; background-color: rgba(128, 128, 128, 0.08); margin-bottom: 15px;">
                    <h3 style="margin-top: 0; margin-bottom: 5px; text-align: center;">Extension Description</h3>
                    <p style="margin: 0; line-height: 1.4;">
                        This tool creates a sequence of images using the same <b>Prompt</b>. 
                        You can customize the <b>Checkpoint</b>, <b>Sampler</b>, and <b>Schedule</b> for each step.<br>
                        <i>Any setting marked as "From previous generation" inherits the value from the row above.</i>
                    </p>
                </div>

                <div style="color: #c0392b; border: 2px solid #c0392b; padding: 10px; border-radius: 8px; background-color: rgba(231, 76, 60, 0.1);">
                    <div style="text-align: center; font-weight: bold; font-size: 1.2em; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 1px;">
                        ⚠️ Important Warning ⚠️
                    </div>
                    <div style="text-align: center;">
                        Please perform a standard generation (without this script selected) at least once after launching Stable Diffusion.
                        If you run this extension immediately after startup without a "dry run", it may fail or crash.
                    </div>
                </div>
                """
            )

            # Setting up the Seed
            use_same_seed = gr.Checkbox(label="Use same Seed for all steps", value=True)
            all_inputs.append(use_same_seed)

            # Hidden counter
            active_rows_count = gr.Number(value=1, visible=False, precision=0)
            all_inputs.append(active_rows_count)

            # String generation (showing only the first one)
            with gr.Group():
                for i in range(self.MAX_ROWS):
                    is_visible = (i == 0)
                    
                    with gr.Row(visible=is_visible) as row:
                        gr.HTML(f"<div style='display:flex; align-items:center; height:100%; justify-content:center;'><b>#{i+1}</b></div>", elem_classes=["min-width-0"])
                        
                        ckpt = gr.Dropdown(label="Checkpoint", choices=options + checkpoints_list, value=self.PREV_OPTION, type="value", scale=3)
                        sampler = gr.Dropdown(label="Sampler", choices=options + samplers_list, value=self.PREV_OPTION, scale=2)
                        scheduler = gr.Dropdown(label="Schedule", choices=options + schedulers_list, value=self.PREV_OPTION, scale=2)
                        
                        all_inputs.extend([ckpt, sampler, scheduler])
                    
                    rows_refs.append(row)

                # Control buttons
                with gr.Row():
                    add_btn = gr.Button("➕ Add Step", variant="primary")
                    remove_btn = gr.Button("➖ Remove Last Step", variant="secondary")

            # --- Interface Logic ---
            
            def update_visibility(count):
                updates = []
                for i in range(self.MAX_ROWS):
                    updates.append(gr.update(visible=(i < count)))
                return updates

            def add_step(current_count):
                new_count = min(current_count + 1, self.MAX_ROWS)
                return [new_count] + update_visibility(new_count)

            def remove_step(current_count):
                new_count = max(current_count - 1, 1) # Минимум 1 строка
                return [new_count] + update_visibility(new_count)

            add_btn.click(
                fn=add_step,
                inputs=[active_rows_count],
                outputs=[active_rows_count] + rows_refs
            )

            remove_btn.click(
                fn=remove_step,
                inputs=[active_rows_count],
                outputs=[active_rows_count] + rows_refs
            )

        return all_inputs

    def run(self, p, use_same_seed, active_count, *args):
        num_steps = int(active_count)
        
        steps_settings = []
        all_groups = [args[i:i+3] for i in range(0, len(args), 3)]
        valid_groups = all_groups[:num_steps]

        for group in valid_groups:
            steps_settings.append({
                "checkpoint": group[0],
                "sampler": group[1],
                "scheduler": group[2]
            })

        # --- Seed Preparation ---
        processing.fix_seed(p)
        original_fixed_seed = p.seed
        original_fixed_subseed = p.subseed
        
        # --- Preparing the initial settings ---
        initial_checkpoint = sd_models.model_data.get_sd_model().sd_checkpoint_info.title
        initial_sampler = p.sampler_name
        initial_scheduler = getattr(p, 'scheduler', 'Automatic')

        current_checkpoint = initial_checkpoint
        current_sampler = initial_sampler
        current_scheduler = initial_scheduler

        combined_processed = None
        
        print(f"\n[All in one go] Steps: {len(steps_settings)}. Same seed: {use_same_seed}")

        for idx, step in enumerate(steps_settings):
            # 1. Inheritance Settings
            if step["checkpoint"] != self.PREV_OPTION:
                current_checkpoint = step["checkpoint"]
            if step["sampler"] != self.PREV_OPTION:
                current_sampler = step["sampler"]
            if step["scheduler"] != self.PREV_OPTION:
                current_scheduler = step["scheduler"]

            # 2. Loading the model
            info = sd_models.get_closet_checkpoint_match(current_checkpoint)
            if info:
                 if sd_models.model_data.get_sd_model().sd_checkpoint_info.title != info.title:
                    print(f"[All in one go] Loading checkpoint: {info.title}")
                    sd_models.reload_model_weights(None, info)
            
            # 3. Application of Seed
            if use_same_seed:
                p.seed = original_fixed_seed
                p.subseed = original_fixed_subseed
            else:
                p.seed = -1 
                p.subseed = -1
                processing.fix_seed(p)

            # 4. Applying Settings
            p.sampler_name = current_sampler
            if hasattr(p, 'scheduler') and current_scheduler != "Automatic":
                p.scheduler = current_scheduler

            print(f"[All in one go] Step {idx+1}/{num_steps} | Seed: {p.seed} | Model: {current_checkpoint}")
            
            # 5. Generation
            processed = processing.process_images(p)
            
            if combined_processed is None:
                combined_processed = processed
            else:
                combined_processed.images.extend(processed.images)
                combined_processed.infotexts.extend(processed.infotexts)
        
        return combined_processed
