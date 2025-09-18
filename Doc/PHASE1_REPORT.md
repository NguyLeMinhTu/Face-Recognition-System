**Phase 1 Report**

- **Scope:**: Compare InsightFace CPU models (`buffalo_s`, `buffalo_l`) on a small image set to choose a CPU-first default for POC.
- **Environment:**: Windows, PowerShell; venv at `d:/FACE/Backend/venv312`; ONNXRuntime (CPUExecutionProvider); InsightFace model packs prepared via `FaceAnalysis.prepare()`.

**Results (summary)**
- **buffalo_s**: avg latency **214.67 ms**, median **214.44 ms**, avg_confidence **0.8027**, errors **0**.
- **buffalo_l**: avg latency **365.39 ms**, median **365.46 ms**, avg_confidence **0.8526**, errors **0**.

**Recommendation**
- **Default model:** `buffalo_s` for CPU-first deployment. Rationale: ~1.6x faster than `buffalo_l` on CPU with only a modest confidence difference; better trade-off for latency-sensitive POC and CPU-only hosts.

**Artifacts produced**
- **CSV:** `results/model_comparison.csv`
- **Markdown:** `results/model_comparison.md`
- **Details JSON:** `results/model_comparison_details.json`

**Reproduce benchmark**
Run inside the project venv (PowerShell):

```powershell
d:/FACE/Backend/venv312/Scripts/python.exe d:/FACE/Backend/explore_models.py --models buffalo_s,buffalo_l --images d:/FACE/Backend/test_images --repeats 10 --max-images 4
```

**Next suggested steps**
- Retry download of `eagle` or locate alternate source if you want a third comparison.
- Run benchmarks on a larger, representative dataset (user images) to validate model choice on target data.
- Create a Phase‑1 commit: add `results/` and `PHASE1_REPORT.md` to version control (I can init and commit if you want).

**Contact / Notes**
- I can create the git commit now or generate a short PR-style patch — tell me which and I'll proceed.
