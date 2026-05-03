# What is PagedAttention?

## Why it exists (THE PROBLEM first)

During autoregressive LLM inference, each sequence stores key and value tensors in a KV cache. Because requests have variable prompt lengths and generate variable numbers of new tokens, allocating one large contiguous block per sequence leaves huge holes of unused memory. This fragmentation kills throughput.

## Definition (very simple)

PagedAttention divides the KV cache into fixed-size blocks (like operating-system pages). A sequence receives blocks on demand, and blocks can be non-contiguous. This virtualizes the KV cache and eliminates most external fragmentation.

## Real-life analogy

A library assigns books to fixed-size shelves rather than giving each patron one giant private bookcase. A patron who needs 35 books gets 2 full shelves and 1 partially used shelf. The empty spots on other shelves can be used by other patrons. No single patron monopolizes a huge contiguous space.

## Tiny numeric example

The KV cache can hold 4,096 tokens total. Without paging, 20 requests each get a 1,024-token contiguous slot. If average sequence length is only 200 tokens, 82% of the cache is wasted. With 16-token pages, those same sequences use only 13 pages each on average (208 tokens), and the remaining pages are available to new requests.

## Common confusion

- **PagedAttention does not reduce the total number of tokens cached.** It only improves how those tokens are packed into memory.
- **It is not the same as swapping to disk.** OS paging moves memory to disk; PagedAttention keeps everything in GPU memory but manages allocation blocks.
- **Blocks are not attention heads.** A block contains tokens across all heads and layers for a slice of the sequence.
- **It does not eliminate all fragmentation.** Internal fragmentation still exists within the last partially filled block of each sequence.
- **PagedAttention is not only for batching.** It also enables memory sharing during parallel sampling and beam search.

## Where it is used in our code

In `src/phase90/phase90_inference_serving.py`, we simulate a fixed-size KV cache and compare naive contiguous allocation against block-based paging. We show that paging achieves significantly higher memory utilization when sequence lengths vary.
