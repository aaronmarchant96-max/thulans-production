/**
 * Multi-Provider Image Generation Engine
 * Features AGY Native (Zero Key Required), OpenAI, Together AI, Fal.ai, and OpenRouter.
 */

import { spawn } from "node:child_process";
import fs from "node:fs";

export async function generateImage({ provider, apiKey, model, prompt, negativePrompt, customEndpoint }) {
  // 1. AGY NATIVE (SYSTEM ENGINE — ZERO KEY REQUIRED)
  if (provider === "agy" || !provider) {
    return new Promise((resolve, reject) => {
      const fullPrompt = negativePrompt ? `${prompt}. Absolutely NO: ${negativePrompt}.` : prompt;
      const cleanPrompt = fullPrompt.replace(/"/g, '\\"');
      const agyCommand = `Use your generate_image tool to generate an image with ImageName "thulan_panel", AspectRatio "16:9", and Prompt "${cleanPrompt}". After the tool runs, print ONLY the absolute file path to the generated image on the last line.`;

      const proc = spawn("agy", [
        "--dangerously-skip-permissions",
        "-p",
        agyCommand
      ]);

      let stdout = "";
      let stderr = "";

      proc.on("error", err => reject(new Error(`AGY generator could not start: ${err.message}. Install AGY locally or select a configured image provider.`)));
      proc.stdout.on("data", d => stdout += d.toString());
      proc.stderr.on("data", d => stderr += d.toString());

      proc.on("close", code => {
        if (code !== 0) {
          return reject(new Error(`AGY generation failed (code ${code}): ${stderr || stdout}`));
        }

        // Find file path in stdout
        const matches = stdout.match(/\/home\/[^\s\n"']+\.(?:jpg|jpeg|png)/g);
        if (!matches || matches.length === 0) {
          return reject(new Error(`No image path returned from AGY: ${stdout}`));
        }

        const generatedPath = matches[matches.length - 1];
        if (!fs.existsSync(generatedPath)) {
          return reject(new Error(`Generated file does not exist at ${generatedPath}`));
        }

        const buffer = fs.readFileSync(generatedPath);
        const b64 = buffer.toString("base64");
        resolve({
          imageBase64: `data:image/jpeg;base64,${b64}`,
          localPath: generatedPath
        });
      });
    });
  }

  // 2. GOOGLE GEMINI / IMAGEN 3 (MANUAL API KEY)
  if (provider === "gemini") {
    if (!apiKey) throw new Error("Gemini API key is required");
    const targetModel = model || "imagen-3.0-generate-002";
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${targetModel}:predict?key=${apiKey}`;

    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        instances: [{ prompt: prompt }],
        parameters: {
          sampleCount: 1,
          aspectRatio: "16:9",
          outputOptions: { mimeType: "image/jpeg" },
          personGeneration: "ALLOW_ADULT",
          safetySetting: "BLOCK_ONLY_HIGH"
        }
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error?.message || `Google Imagen error: ${res.statusText}`);
    return {
      imageBase64: `data:image/jpeg;base64,${data.predictions[0].bytesBase64Encoded}`
    };
  }

  // 3. OPENAI (DALL-E 3)
  if (provider === "openai") {
    if (!apiKey) throw new Error("OpenAI API key is required");
    const res = await fetch("https://api.openai.com/v1/images/generations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: model || "dall-e-3",
        prompt: prompt,
        size: "1792x1024",
        quality: "standard",
        n: 1,
        response_format: "b64_json"
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error?.message || `OpenAI error: ${res.statusText}`);
    return {
      imageBase64: `data:image/png;base64,${data.data[0].b64_json}`
    };
  }

  // 4. TOGETHER AI (FLUX)
  if (provider === "together") {
    if (!apiKey) throw new Error("Together AI key is required");
    const res = await fetch("https://api.together.xyz/v1/images/generations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: model || "black-forest-labs/FLUX.1-schnell",
        prompt: prompt,
        negative_prompt: negativePrompt || "",
        width: 1344,
        height: 768,
        steps: 4,
        n: 1,
        response_format: "b64_json"
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error?.message || `Together AI error: ${res.statusText}`);
    return {
      imageBase64: `data:image/png;base64,${data.data[0].b64_json}`
    };
  }

  throw new Error(`Unsupported provider: ${provider}`);
}
