# All in one go
All in one go is an extension for Stable Diffusion that allows you to generate multiple images in a row, with different "Checkpoints, Samplers or Schedulers" in one turn.

# The reason creating extension
When generating images, I typically use the sampling methods DPM++ 2M or Euler a. The reason for this is that I'm well aware of approximately what results I'll achieve with these samplers. Using other samplers seems tedious to me because it requires constantly changing the sampler after each generation and generating again. Therefore, I struggle to understand how my images turn out when using other samplers. Because of this, I'm pretty much limiting my image options. Given that most images are created using these samplers, perhaps I'm not alone in my approach.

I tried looking for an extension that would allow automatic switching between samplers but either I didn't search thoroughly enough or such extensions simply don't exist. Eventually, I decided to create one myself.

I'll be honest—I am far from being a programmer, so I wrote the extension primarily by utilizing AI assistance, editing it slightly when the AI couldn't implement what I needed.
Initially, this extension was intended solely for personal use. As I refined certain aspects, I shared it with acquaintances for testing purposes. They really liked it, which led me to decide on making it publicly available.

As mentioned earlier, since I'm not a professional developer, I won't be actively maintaining this extension. However, it's designed in such a way that updates shouldn't be necessary unless there are major changes within Stable Diffusion itself.
If anyone encounters critical bugs, I'll try to fix them, though I can't guarantee anything.
Additionally, if you wish to contribute to its development, I'd appreciate your input. Feel free to suggest various improvements or even develop your project based on this.

# How to use

In the Stable Diffusion WebUI architecture, the only stable way to intercept the main generation cycle and run your own sequence is through the Scripts interface. 
Therefore, you will find this extension in the Script.

<img width="668" height="87" alt="{C1AE0E1B-9225-4AEF-AEF3-718FC898F51C}" src="https://github.com/user-attachments/assets/82a734d4-9713-44bd-adc5-879025fb80ef" />
<img width="675" height="198" alt="{20BA1823-C754-4724-A4F1-85AA9BB20422}" src="https://github.com/user-attachments/assets/e1cc37d5-7964-4691-b4af-e23fc0e437a1" />

After selecting the extension, it may open with a delay if only a short time has passed since launching Stable Diffusion. Initially, I thought this might be an issue with the extension itself, but it's more likely that Stable Diffusion takes some time to load scripts.
After that, you will be greeted by the extension menu.

<img width="667" height="567" alt="изображение" src="https://github.com/user-attachments/assets/790eedec-9ad5-493e-b2f4-31f5204618fd" />

By default, the extension uses the Seed of the first generated image from the stream for all generations. If you want to use different Seeds for each image, then uncheck the box.

The buttons allow you to add or remove steps. There is a maximum limit of 20 steps. This restriction is due to incorrect behavior when dealing with a large number of steps. Many users, including myself, have noticed that after step 30, the workload significantly increases. At 48 steps, image generation froze entirely on my system.
This issue occurred in older versions of the extension, and I haven't tested whether there's increased load beyond 30 steps in the current version. A friend informed me that he experienced normal performance levels beyond 30 steps. Nevertheless, as a precautionary measure, I've kept the limit at 20 steps.
If you want to increase the number of steps, edit the file <code>webui\extensions\all-in-one-go\scripts\all_in_one_go.py</code> in the extension directory and change the line <code>self.MAX_ROWS = X</code>, where X represents the desired number of steps.

Checkpoints and Samplers fetch data directly from your Stable Diffusion instance, whereas the Schedule option is limited to just six universal options. Most modern samplers already come equipped with built-in fixed schedules optimized specifically for their operation. Therefore, choosing a schedule isn't particularly necessary anymore, except possibly for older versions of Stable Diffusion or specific Samplers.

Each step defaults to inheriting settings from the previous step. In other words, the first step will take the settings you've configured in Stable Diffusion, the second step will inherit from the first, the third from the second, and so forth.
