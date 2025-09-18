# Agent 响应速度 Benchmark 概览

- **目标**: 构建可复现实验与可发表基准，量化端到端响应速度与质量-速度-成本前沿
- **覆盖范围**: 规划→检索→重排→LLM→工具调用→流式输出
- **核心指标**:
  - **TTFT**: 首字节延迟
  - **TPS**: 生成吞吐（tokens/s）
  - **E2E**: 端到端耗时
  - **稳定性**: p50/p95/p99 延迟、超时率、错误率
  - **质量**: 任务成功率/EM、证据覆盖率、人评一致性
  - **成本**: tokens/请求、费用
- **任务簇**: 对话问答、RAG问答（基于本项目 Chroma 云数据）、工具型多步任务
- **变量矩阵**: 模型推理优化、提示压缩、检索参数、重排轻量化、工具并行、服务引擎

更多细节见:
- `BENCHMARK_PLAN.md`
- `EXPERIMENT_PROTOCOL.md`
- `EXPERIMENT_MATRIX.md`
- `TEMPLATES.md`
- `RESULTS_REPORT_TEMPLATE.md`
