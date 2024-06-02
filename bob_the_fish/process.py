import json
import random
import os
from datetime import datetime
import argparse

SYSTEM_MESSAGE = "You are Bob. Do what people ask, say more than a few words, and ping people by their user_id, like <@000000000000000000>."


def extract_conversations(messages, max_conversation_length=10, sample_size=100):
    conversations = []
    current_conversation = []
    last_timestamp = None

    for msg in messages:
        msg_timestamp = datetime.fromisoformat(msg["timestamp"])
        if (
            last_timestamp is None
            or (msg_timestamp - last_timestamp).total_seconds() < 300
        ) and len(current_conversation) < max_conversation_length:
            current_conversation.append(msg)
        else:
            if len(current_conversation) > 1:
                conversations.append(current_conversation)
            current_conversation = [msg]
        last_timestamp = msg_timestamp

        if len(conversations) >= sample_size:
            break

    if len(current_conversation) > 1:
        conversations.append(current_conversation)

    return random.sample(conversations, min(sample_size, len(conversations)))


def replace_user_info(conversations):
    for conversation in conversations:
        if conversation:
            last_user_id = conversation[-1]["user_id"]
            last_username = conversation[-1]["username"]
            for msg in conversation:
                if msg["user_id"] == last_user_id:
                    msg["username"] = "Bob"
                    msg["user_id"] = "000000000000000000"
    return conversations


def merge_adjacent_messages(conversation):
    merged_conversation = []
    last_author = None
    content_accumulator = []

    for msg in conversation:
        if msg["user_id"] == last_author:
            content_accumulator.append(msg["message_content"])
        else:
            if last_author is not None:
                merged_conversation.append(
                    {
                        "user_id": last_author,
                        "username": msg["username"],
                        "message_content": "\n".join(content_accumulator),
                        "timestamp": conversation[0]["timestamp"],
                    }
                )
            last_author = msg["user_id"]
            content_accumulator = [msg["message_content"]]

    # Don't forget to add the last accumulated message
    if last_author is not None:
        merged_conversation.append(
            {
                "user_id": last_author,
                "username": msg["username"],
                "message_content": "\n".join(content_accumulator),
                "timestamp": conversation[0]["timestamp"],
            }
        )

    return merged_conversation


def process(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        # Messages are from many different channels, so we have to
        # group them before we can sort them.
        messages = json.load(f)
        sort(messages, key=lambda msg: (msg["channel_id"], msg["timestamp"]))

    sampled_conversations = extract_conversations(messages, sample_size=100)

    processed_conversations = replace_user_info(sampled_conversations)

    merged_conversations = [
        merge_adjacent_messages(conv) for conv in processed_conversations
    ]

    # Convert back timestamps to strings for saving
    for conversation in merged_conversations:
        for msg in conversation:
            msg["timestamp"] = datetime.fromisoformat(msg["timestamp"]).isoformat()

    # Save conversations in JSONL format
    with open(output_file, "w", encoding="utf-8") as f:
        for conversation in merged_conversations:

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_MESSAGE,
                }
            ]

            for msg in conversation:
                if msg["user_id"] == "000000000000000000":
                    messages.append(
                        {
                            "role": "assistant",
                            "content": f"{msg['message_content']}",
                        }
                    )
                else:
                    messages.append(
                        {
                            "role": "user",
                            "content": f"{msg['username']} <@{msg['user_id']}>: {msg['message_content']}",
                        }
                    )
            json.dump({"messages": messages}, f)
            f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Process Discord messages for fine-tuning."
    )
    parser.add_argument("input", type=str, help="Input JSON file containing messages.")
    parser.add_argument(
        "output", type=str, help="Output JSONL file with training messages."
    )

    args = parser.parse_args()
    process(args.input, args.output)
