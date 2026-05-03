# Phase 14 Summary: LSTM — Long Short-Term Memory

## What This Phase Taught

RNNs forget the distant past because their hidden state gets overwritten at every step. LSTMs solve this with a protected cell state (long-term memory) and three gates that control what to forget, what to remember, and what to output.

## Key Concepts

- **Cell State**: A protected conveyor belt that can preserve information for hundreds of steps
- **Forget Gate**: Decides what information to remove from the cell state
- **Input Gate**: Decides what new information to store in the cell state
- **Output Gate**: Decides what to output based on the cell state
- **LSTM**: A type of RNN that uses gates and a cell state to selectively remember and forget

## The Code

`src/phase14/phase14_lstm.py` — A complete LSTM cell with all four gates, backpropagation through the LSTM, and a controlled demonstration showing that the LSTM cell state preserves a value across 50 steps while a vanilla RNN's hidden state decays to near zero.

## Results

The controlled demonstration clearly showed the architectural difference:
- LSTM cell state after 50 steps: 4.99 (preserved from 5.0)
- RNN hidden state after 50 steps: 0.003 (decayed to near zero)

This proves that the LSTM architecture is designed for long-term memory, regardless of training.

## The Analogy

An LSTM is like an airport baggage carousel. Bags (information) go around and around. Security (forget gate) removes dangerous bags. New arrivals (input gate) add bags. But the carousel itself keeps running, preserving most bags for hours.

## Connection to Previous Phase

Phase 13 built a vanilla RNN for short sequences. Phase 14 solves the RNN's fatal flaw: forgetting the distant past.

## Connection to Next Phase

Phase 15 asks: "Words are just numbers to my network. How do I give words MEANING?" We will learn about word embeddings.
