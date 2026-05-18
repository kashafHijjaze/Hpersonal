# Hijjaze AI Image Studio

Hijjaze AI Image Studio is a premium Flask web application for AI image generation, 2K/3K/4K enhancement, upscaling, background removal, photo restoration, prompt workflows, dashboard views, authentication screens, SEO pages, and responsive commercial UI.

## Features

- Text-to-image studio with prompt, negative prompt, styles, ratios, HD toggles, random prompts, copy prompt, prompt history, and download.
- AI image enhancer with drag/drop upload, 2K/3K/4K modes, denoise, face sharpening, restoration, before/after compare, zoom preview, and download.
- Advanced tools area for background removal, object removal, portrait enhancement, anime conversion, sketch conversion, colorizing, and super-resolution.
- Dashboard UI for generated history, enhanced history, downloads, favorites, profile, settings, API usage, and storage management.
- Login/register pages with Google login UI, forgot password link, email verification note, and API-auth scaffold.
- SEO-ready meta tags, Open Graph, Twitter cards, canonical URL, semantic sections, FAQ/Product/Organization schema, `robots.txt`, and `sitemap.xml`.
- Responsive glassmorphism interface using Bootstrap 5, GSAP, Font Awesome, neon gradients, dark/light mode, counters, animated loaders, and hover states.

## Screenshots

Run the project and open:

- Home and live AI preview: `http://localhost:5000/`
- Generator: `http://localhost:5000/#generator`
- Enhancer and upscaler: `http://localhost:5000/#enhancer`
- Auth: `http://localhost:5000/login`

## Installation

```bash
cd HijjazeAIStudio
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Open `http://localhost:5000`.

## AI Tools Explanation

The project is built so heavy AI libraries are optional at runtime:

- Stable Diffusion / HuggingFace: set `HUGGINGFACE_API_TOKEN` and `HUGGINGFACE_IMAGE_MODEL` to enable real text-to-image API generation.
- Real-ESRGAN: install compatible Real-ESRGAN weights and set `REALESRGAN_MODEL_PATH`; the service layer is prepared for model-backed super-resolution.
- OpenCV: used for denoising, CLAHE contrast correction, cubic upscaling, and sharpening.
- Pillow: used for fallback upscaling, color/contrast/sharpness enhancement, and branded preview image generation.
- rembg: used for U2-Net background removal when installed.
- PyTorch, Diffusers, Transformers: included for local Stable Diffusion and advanced pipelines.

When a remote model or large local checkpoint is not configured, the app uses graceful fallbacks so the website remains usable during development.

## API Setup

Create `.env` from `.env.example`:

```bash
SECRET_KEY=your-production-secret
SITE_URL=https://your-domain.com
HUGGINGFACE_API_TOKEN=hf_your_token
HUGGINGFACE_IMAGE_MODEL=stabilityai/stable-diffusion-xl-base-1.0
```

Production auth should replace the demo `/api/auth` route with OAuth, hashed passwords, email verification, password reset, sessions, and CSRF protection.

## SEO Setup

- Update `SITE_URL` in `.env`.
- Replace `localhost` in `sitemap.xml` and `robots.txt` with your production domain.
- Add a real `static/images/og-preview.png` for social sharing.
- Keep FAQ/Product/Organization schema aligned with live pricing and product claims.

## Deployment

For a basic production deployment:

```bash
pip install -r requirements.txt
set FLASK_ENV=production
waitress-serve --listen=0.0.0.0:8000 app:app
```

Recommended production stack:

- Gunicorn or Waitress behind Nginx
- GPU worker for Stable Diffusion / Real-ESRGAN
- Object storage for uploads and outputs
- Database for users, prompts, jobs, downloads, favorites, and API usage
- Queue system such as Celery/RQ for long AI jobs
- CDN for static assets

## Requirements

Core stack:

- Python 3.10+
- Flask
- Bootstrap 5
- GSAP
- Font Awesome
- OpenCV
- Pillow
- PyTorch / Diffusers / Transformers
- Real-ESRGAN
- rembg

## Credits

Built with Flask, Bootstrap, GSAP, Font Awesome, Pillow, OpenCV, rembg, HuggingFace, Diffusers, PyTorch, and Real-ESRGAN-ready architecture.

## License

MIT License. Review model and dataset licenses separately before commercial deployment.
