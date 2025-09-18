# 模板与规范

## 配置模板（YAML）
```yaml
experiment_id: exp_YYYYMMDD_HHMM
seed: 42
workload:
  rps: [1, 5, 10, 20]
  duration_s: 180
  repeats: 3
suite:
  tasks: [dialog_qa, rag_qa, tool_multi]
variables:
  speculative_decoding: [off, on]
  prompt_compression_ratio: [0, 0.2, 0.4]
  retriever:
    top_k: [5, 10, 20]
    hnsw_ef_search: [64, 128]
  reranker: [off, base, large]
  tools_parallel: [off, on]
  serving: [native, vllm]
logging:
  csv_path: results/exp_log.csv
  aggregate_path: results/exp_agg.csv
```

## 结果日志CSV头
```csv
timestamp,request_id,task,variant,concurrency,ttft_ms,tps_tokens_per_s,e2e_ms,plan_ms,retrieval_ms,rerank_ms,llm_ms,tools_ms,stream_ms,input_tokens,output_tokens,cost_success,success,err_type
```

## 聚合表CSV头
```csv
variant,task,rps,ttft_p50,ttft_p95,ttft_p99,tps_mean,e2e_p50,e2e_p95,e2e_p99,success_rate,cost_per_req
```

## 图表建议
- 质量-速度前沿: x=E2E y=成功率，标注成本
- 延迟箱线: 各variant的p50/p95/p99
- CDF: TTFT/E2E 分布

## 人评表单要点
- 准确性/相关性/完整性/流畅性 1-5分
- 证据引用是否充分（RAG）
