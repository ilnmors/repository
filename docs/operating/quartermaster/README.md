# quartermaster

| Item | Value |
| --- | --- |
| Host | app (10000), internal only: `quartermaster.app.ilnmors.internal` |
| Version (2026-11-15) | v1.9.1, rebuilt locally (`ilnmors.internal/app/quartermaster`) |
| Backends | llama-server b10796 (Vulkan, from the upstream image), sd-server master-1098 (Vulkan) |

## Notes

- Replaced the separate llama.cpp and stable-diffusion.cpp servers on 2026-11-14. Open WebUI uses it for chat, embeddings and images.
- All four models (LFM2.5-24B-A2B, LFM2.5-VL-3B, LFM2.5-Embedding-350M, zImage-moodyRealMix) stay loaded together in one routing group and are preloaded at start.
- The image is rebuilt on Ubuntu 26.04 with the Mesa Vulkan drivers: upstream ships the Vulkan loader only, so the backends fell back to the CPU. The bundled sd-server (master-841) rendered noise on the Iris Xe; master-1098 renders correctly but needs glibc 2.43.
- 512×512 images render correctly. 1024×1024 renders noise on the Iris Xe, with or without diffusion flash attention (2026-11-15), so Open WebUI requests 512×512 (`IMAGE_SIZE`). 768×768 is untested. Recheck larger sizes on the RX 7900 XT.
- sd-server has no `/health`; its readiness check is `/v1/models`.
- The dashboard runs with `-admin-open`, so it has no public route.
- Unload a model with `POST /api/models/unload/<id>`.
- Qwen3.8-Flash-Next (`qwen3.8-flash-next-ista`, ISTA GSQ-RCO IQ2_XS; a few Chinese words in Korean answers are accepted, IQ3_XXS was only slightly better and a third slower; the IQ3_XXS and Q2_0 files are kept in DATA) is served by Strata, bundled in the image from its release image (`releases.yaml`, `build.strata`): the engine needs only glibc from the system, so it runs beside the Vulkan backends. Quartermaster starts the image's entrypoint as the model command; the entrypoint is patched to serve on loopback without a key and to keep its state in `/data/strata`. The container gets `/dev/kfd`, unlimited memlock and a 2 GB `/dev/shm` for it.
- Strata on the RX 7900 XT (2026-11-20/21, 32k context, DFlash2, tuned preset, `pool-workers=10`, pinned resident experts, learned expert profile): decode IQ2_XS 44-59 t/s, IQ3_XXS 35-40, Q2_0 47-64. On the evaluation sample (GSM8K 60, HumanEval 40, KMMLU 90) IQ2_XS scored 83.2%, IQ3_XXS 83.7%, Q2_0 81.6% (weaker in Korean history).
