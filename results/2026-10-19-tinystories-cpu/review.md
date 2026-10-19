# TinyStories CPU Learning Baseline — Output & Quality Review

This review documents all 27 unedited prompt/response pairs and the loss trajectory from our 8,192-update TinyStories CPU baseline run (`step_00008192_gen_000028`). While validation loss dropped to `1.7043`, the model failed the strict story-quality rubric (2/24 overall passes), providing a clear baseline for testing architectural, data, or decoding improvements.

## Terminal identity and evaluation

Run `tinystories-r7-continued`; immutable generation `step_00008192_gen_000028`.

Checkpoint SHA256: `d5ba0e06c91d7a864264c5af411ced1c1b1c4e136632d71cd0a7b4309a728149`

8,192 updates; 33,554,432 supervised targets. Native full-state verification valid. Standalone evaluation matches training terminal evaluation: loss **1.7043116390705109**, perplexity **5.497600031351529**, 16,384 targets in 16 batches. This is a fixed validation slice, not a broad capability benchmark.

Weights SHA256: `f1d8c8906c8e8644ac66adc10fd74bd345c42561fa7c736cb06331e1521523bf`. Training state SHA256: `82367a63409ed90723d3925a6d7f5677a42ec4c6bd98b7609301ce25768c6deb`.

Tokenizer SHA256: `a30e7eeec9e085eb6df1cbc377bb7f11d1e58a6a30890856ea74b816352efefa`. Prepared manifest SHA256: `eb6c7d63d5122209e5a923ebbb1a5bb339376dad80ffcbb5ed28c70fb10c7cdc`.

## Loss trajectory

| Update | Validation loss |
|---:|---:|
| 0 | 8.3688669205 |
| 1024 | 2.5097619742 |
| 1406 | 2.3396986648 |
| 2048 | 2.1708794609 |
| 3072 | 2.0008934066 |
| 4096 | 1.8838655800 |
| 5120 | 1.8195766062 |
| 6144 | 1.7596859857 |
| 7168 | 1.7239373997 |
| 8192 | 1.7043116391 |

Last-256-update mean recorded train losses:

| Window ending | Mean train loss |
|---:|---:|
| 1024 | 2.80671135 |
| 2048 | 2.43890692 |
| 4096 | 2.12630403 |
| 6144 | 1.94041347 |
| 8192 | 1.88325411 |

All recorded lineage metrics are finite; reported optimizer overflow retries are zero. Validation repeated at continuation boundaries exactly reproduced the saved values. Training/validation losses are measured on different batches and are not a controlled overfitting test.

## Evidence-supported limitations versus untested explanations

| Area | Observed evidence | Interpretation and uncertainty |
|---|---|---|
| Data quantity and reuse | 50,000 selected training documents; 11,370,444 packed train tokens; 11,370,240 usable supervised targets per loader pass. Native final exposure is 2.951075 effective passes (two completed passes plus part of a third). Tokenizer was fitted on 17,856 training documents / 15,998,933 UTF-8 bytes under its 16 MB cap. Validation has 512 documents / 104,675 packed tokens. | Reuse is measured; additional updates would increasingly reuse this finite supply. Limited diversity is a plausible constraint, but no larger-data controlled run establishes causation or the gain from more data. Exact deduplication does not establish semantic disjointness or a train-disjoint prompt benchmark. |
| Model capacity/depth | Dense decoder: 4 layers, width 256, FFN 768, 4 heads, vocabulary 4096, tied embeddings; 4,458,752 unique parameters. Training length 256; architectural context 512. | The observed model often loses entities and plot context. Limited capacity/depth is a plausible contributor, not a proven cause: no depth/width ablation was run. Larger architecture or longer context has no measured benefit in this experiment. |
| Decoding/cache parity | Greedy (0/0) and sampled (0.7/40) decoding both fail the quality gate. All outputs use seed42, use_cache=true, strict_context=true, no stop sequences. The fixed prompt-plus-allowance bound is at most212 tokens. | Tested sampling changes do not solve the problem. No cached-versus-uncached parity test was run, so a cache-path defect is neither demonstrated nor ruled out. Matching standalone/terminal evaluation does not establish autoregressive cache parity. No retained sampled token IDs or explicit EOS finish reason: short responses are not labeled as directly observed EOS events. |
| Optimizer/schedule/token budget | AdamW peak0.0006/floor0.00006, warmup256, original cosine horizon8192, FP32 deterministic CPU, microbatch4 x accumulation4, seq256 =4096 targets/update. Full optimizer/RNG/cursor restoration was verified; horizon was not reset. Loss continued falling from1.72394 at7168 to1.70431 at8192. | Continued NLL learning supports remaining learning potential, but does not prove extra steps will meet the story gate. No alternative learning-rate schedule, optimizer, token budget or fresh-data extension was tested. Finite metrics and zero overflow do not rule out every implementation defect. |
| Observed story behavior | Repeated sentence loops, character renaming, object substitutions, and dropped prompt problems occur across the full retained fixed set. | These are direct failure evidence. The experiment does not isolate one root cause, and lower teacher-forced loss is insufficient evidence of coherent free generation. |

Follow-up diagnostics (such as KV-cache parity checks, larger training subsets, or width/depth ablations) can be run as separate comparisons against this baseline.

## Decoding and resource evidence

The 24 scored outputs use 192 maximum new tokens: one greedy and one sampled output for each of 12 frozen prefixes. The first six are development prefixes; the final six were withheld from model selection. Three additional website baselines use the first three prefixes, greedy decoding, and 48 maximum new tokens; they are excluded from quality scoring. All native identities and prompt token counts matched.

This continuation trainer: 9895.283 seconds; successful lineage trainer invocations: 11861.468 seconds. Training peak sampled RSS: 974,274,560 bytes. All27 generation invocations: 89.644 seconds total, including startup/loading/verification; sampled peak RSS 450,138,112 bytes. These are process wall times, not isolated decode latency.

All 35 session steps completed within the configured wall-clock budget.

All35/35 supervised slots succeeded with complete evidence. Container exit0; cleanup verified; no active training host claim or container remains. Memory and retained storage use sampled observations with stop response, not hard caps. The image enforced the eight-CPU quota; networking remained none. Prior attempts, refusals and reboot/pause evidence remain preserved.

| Output | Prompt tokens | Max new | Process seconds | Peak sampled RSS bytes |
|---|---:|---:|---:|---:|
| final-greedy-1 | 18 | 192 | 3.474875 | 444395520 |
| final-sampled-1 | 18 | 192 | 3.683891 | 445583360 |
| final-greedy-2 | 16 | 192 | 3.420518 | 445145088 |
| final-sampled-2 | 16 | 192 | 3.090262 | 445177856 |
| final-greedy-3 | 16 | 192 | 3.219199 | 443953152 |
| final-sampled-3 | 16 | 192 | 3.466837 | 445485056 |
| final-greedy-4 | 18 | 192 | 3.460551 | 444149760 |
| final-sampled-4 | 18 | 192 | 3.344502 | 444637184 |
| final-greedy-5 | 20 | 192 | 3.418776 | 443813888 |
| final-sampled-5 | 20 | 192 | 3.422438 | 444534784 |
| final-greedy-6 | 20 | 192 | 3.420544 | 444375040 |
| final-sampled-6 | 20 | 192 | 3.468353 | 445341696 |
| final-greedy-7 | 20 | 192 | 3.431637 | 444735488 |
| final-sampled-7 | 20 | 192 | 3.558220 | 445485056 |
| final-greedy-8 | 18 | 192 | 3.360354 | 444694528 |
| final-sampled-8 | 18 | 192 | 3.168962 | 450138112 |
| final-greedy-9 | 14 | 192 | 3.157607 | 443981824 |
| final-sampled-9 | 14 | 192 | 3.552604 | 444776448 |
| final-greedy-10 | 17 | 192 | 3.452961 | 443994112 |
| final-sampled-10 | 17 | 192 | 3.135659 | 446185472 |
| final-greedy-11 | 20 | 192 | 3.068038 | 444014592 |
| final-sampled-11 | 20 | 192 | 3.267137 | 444600320 |
| final-greedy-12 | 18 | 192 | 3.145754 | 444698624 |
| final-sampled-12 | 18 | 192 | 3.181674 | 444948480 |
| website-baseline-1 | 18 | 48 | 3.094058 | 443752448 |
| website-baseline-2 | 16 | 48 | 3.096927 | 444293120 |
| website-baseline-3 | 16 | 48 | 3.081508 | 444334080 |

## Per-output assessment

Assistant provisional rubric assessment, not independent human clearance. A quality pass requires relevance, readable sentence flow, character/object consistency and event continuity, without a repeated-sentence/semantic loop. Understandable endings are counted separately; a closing sentence does not repair other failures. The borderline sampled-3 output is counted generously.

**Quality:2/24 (required20); held-out-prefix subset:1/12 (required10); understandable endings:17/24 (required18). Gate failed.**

| Output | Relevant | Readable | Consistent | Continuity | Loop | Ending | Pass | Reason |
|---|---|---|---|---|---|---|---|---|
| greedy-1 | yes | no | no | no | yes | no | no | Starts with the red ball, then throws the ball at itself and loops I want the red ball until cutoff. |
| sampled-1 | no | yes | no | no | no | no | no | Box contents become flowers; the red ball disappears and the output ends mid-event at a truck. |
| greedy-2 | no | no | no | no | yes | no | no | Bird rescue disappears; Sam gives a stick to Sam, then repeated hole-making ends mid-sentence. |
| sampled-2 | yes | yes | no | no | no | yes | no | Readable rescue and ending, but the declared dry stick becomes a leaf without explanation. |
| greedy-3 | yes | yes | no | yes | no | yes | no | Sharing arc and ending are clear, but the apple is explicitly both not good and good, then described as good at sharing. |
| sampled-3 | yes | yes | yes | yes | no | yes | yes | Borderline pass: Mia, Ben and apple sharing persist with a recognizable ending; awkward stickers/toys/cookie and park phrasing weaken fluency. |
| greedy-4 | yes | yes | no | no | no | yes | no | Eli becomes Timmy; mother says the cup is not a toy but invites playing with it. |
| sampled-4 | yes | yes | no | no | no | yes | no | Eli becomes Ben and the broken cup becomes associated with a car; moral ending does not repair identity drift. |
| greedy-5 | yes | no | no | no | yes | yes | no | Seed helps itself; near-duplicate seed-was-so-happy passages replace coherent growth events. |
| sampled-5 | no | no | no | no | no | yes | no | Ada/seed care is replaced by fairy, bird and flower identities; fairy speaks with fairy. |
| greedy-6 | no | no | no | no | yes | no | no | Fair toy sharing is dropped for an extended identical box/key sentence loop and cutoff. |
| sampled-6 | no | no | no | no | yes | yes | no | Toy/fairness goal disappears into repetitive other-kids references and conflicting desires; generic play ending. |
| greedy-7 | yes | no | no | no | yes | no | no | Mitten becomes a rope; repeated too-heavy sentences and self-referential rope actions end incomplete. |
| sampled-7 | yes | no | no | no | no | no | no | Noah changes into a girl; ownership and mother instructions conflict; ends incomplete. |
| greedy-8 | no | yes | no | no | no | yes | no | Hole problem is ignored; animals are asked a question but boat replies; generic adventure ending. |
| sampled-8 | yes | no | yes | yes | no | yes | no | Attempts a stick repair and ends, but opening use the hole to take a hole out is not intelligible sentence flow. |
| greedy-9 | no | yes | yes | no | no | yes | no | Rain/kitten concern is dropped for disconnected monster chase fragments; a final disappearance supplies closure. |
| sampled-9 | no | no | no | no | yes | yes | no | Kitten disappears; bird talks to bird and flies with bird in repetitive gratitude/singing exchanges. |
| greedy-10 | no | no | no | no | yes | no | no | Watering promise disappears; Ben thanks Ben with repeated help dialogue, ending at a cutoff. |
| sampled-10 | no | yes | yes | no | no | yes | no | Readable but unrelated family/animal moral; never resolves watering the flowers. |
| greedy-11 | yes | yes | yes | yes | no | yes | yes | Short understandable crown-giving and friendship ending; recipient is implicit and underspecified. |
| sampled-11 | yes | no | no | no | no | yes | no | Paper crown becomes a flower and yellow crayon; broken reference/grammar despite a closing sentiment. |
| greedy-12 | yes | yes | yes | no | yes | yes | no | Repeats lights go up and down three times without resolving the puppet-show problem; pride ending. |
| sampled-12 | no | no | no | no | no | yes | no | Power/puppet problem changes to a cake; opening make the difference a goal is unintelligible. |

## All 24 full prompt/output pairs and three baselines

# Final fixed story outputs

All outputs below are unedited native continuations. The original raw JSON, stderr and supervisor receipt accompany each output. No retries or resampling.

## final-greedy-1

Prompt: Lily put her red ball in a blue box. Later, she opened the box and

```text
 saw a big, red ball. She wanted to play with it. She asked her mom if she could have it. Her mom said yes, but she had to be careful.

Lily took the red ball and threw it at the ball. She did not want to share. She said, "No, I want the red ball. It is mine." Her mom said, "No, Lily, you can't have the red ball. You have to share and be nice."

Lily was sad. She did not want to share. She wanted the red ball. She said, "No, I want the red ball. I want the red ball. I want the red ball. I want the red ball. I want the red ball. I want the red ball. I want the red ball. I want the red ball. I want the red ball. I want the red ball. I want the red ball. I want the
```

## final-sampled-1

Prompt: Lily put her red ball in a blue box. Later, she opened the box and

```text
 saw some pretty flowers. She wanted to pick it and take it home. She took the flowers and the flowers and put them in the box. She put them in a jar and took it home. She put the flowers back on the box. She waited for the flowers to grow.

She made a big, beautiful flower with a star and a paper. She put the flowers on the paper and the flowers in a bowl. She took some yellow flowers and put them in the jar. She said to her mom, "Mom, can we get one?"

Her mom smiled and said, "Yes, we can, Lily. But first, let's go to the store. Maybe we can find another place to buy."

Lily and her mom went to the store. They went to the store and bought a big box. They found two toys and books. They were very happy.

But then, Lily saw a big truck
```

## final-greedy-2

Prompt: Sam saw a small bird stuck in a puddle. He found a dry stick and

```text
 put it on the ground. He picked up the stick and put it in his pocket.

"Here, Sam, you can have this stick," said Sam. He took the stick and put it in his pocket. He gave it to Sam and said, "Here, you can have this stick. It is not a toy. It is a stick. It is a stick that can make a hole in the ground. It can make a hole in the ground. Do you want to try it?"

Sam nodded and said, "Yes, I do. I want to play with the stick. It is fun and shiny. I want to play with it."

They took turns to make the hole. They pretended it was a boat. They made a hole in the hole. They made a hole in the hole. They put the stick in the hole. They hoped the hole would not be too heavy. They hoped the hole would
```

## final-sampled-2

Prompt: Sam saw a small bird stuck in a puddle. He found a dry stick and

```text
 used the leaf to help the bird out. The bird was very happy and thanked Sam. They became friends and played together every day.
```

## final-greedy-3

Prompt: Mia wanted to share her last apple with Ben. She cut it in two and

```text
 gave it to Ben.

"Here you go, Ben. You can have this. It is not a good one. It is a good one. It is very good at sharing."

Ben smiles and says, "Thank you, Mia. You are very kind. You are a good friend."

Mia smiles and says, "You're welcome, Ben. You are a good friend too. I like you too."

They hug and play with the other kids. They are happy. They have a new friend.
```

## final-sampled-3

Prompt: Mia wanted to share her last apple with Ben. She cut it in two and

```text
 put some stickers on it. "Here, it is your apple. It is juicy and sweet."

Ben is happy. He has found a new apple and a lot of toys. He gives Mia a cookie and a cookie each. "Thank you, Mia. You are a good friend. Thank you for sharing it with me."

Mia smiles. She is happy. She hugs Ben and says, "You're welcome, Ben. You are a good friend. Let's play together."

Ben smiles too. He says, "Okay, Mia. I like the apple. Maybe I'll share it with you."

They play with the apple at the park. They share it and play with the park. They are happy.
```

## final-greedy-4

Prompt: Eli broke his favorite cup. He decided to tell the truth about what happened.

```text
 He said, "I'm sorry, mom. I didn't mean to break it. I just wanted to play with my cup."

His mom hugged him and said, "It's okay, Timmy. I'm glad you're not mad at me. But you have to be careful with your cup. It's not a toy. It's just a cup."

Timmy nodded and said, "Okay, mom. I will be careful. I will be careful with my cup."

His mom smiled and said, "That's good, Timmy. Now, let's go play with your cup. It's not a toy, but it's still fun to play with."

Timmy smiled and said, "Okay, mom. I love cupcakes. And I love cups too."
```

## final-sampled-4

Prompt: Eli broke his favorite cup. He decided to tell the truth about what happened.

```text


"I'm sorry, mom," he said. "I wanted to help you. I didn't mean to break it. I just wanted to keep it."

His mom smiled and hugged him. "I know, Ben. Don't worry. It was an accident. It was just like you can fix it. But next time, be careful with the cup, okay?" she said.

"Okay, mom," Ben said. He was happy. He had made his favorite cup that was perfect for his car. He knew it was a special kind and honest boy. He learned to be more careful with his car. He also learned to listen to his mom.
```

## final-greedy-5

Prompt: Ada planted a seed in a small pot. Every day she carefully looked after it.

```text


One day, she decided to take a break and put the seed in a special place. She was so happy and excited to see the seed. She put it in a special place and watched it grow.

The seed was so happy to be there. It was so beautiful and it was so beautiful. She was so happy and proud of her work.

The seed was so happy that it had been able to help the seed. It was so happy and it was so proud of itself.

The seed was so happy that it had been able to help the seed. From then on, the seed was always happy to help its friends.
```

## final-sampled-5

Prompt: Ada planted a seed in a small pot. Every day she carefully looked after it.

```text


One day, a magical fairy came to visit. She was so small that she could see the bird. She looked at the fairy and said, "Hello flower! I have a special flower for you. I made you a special flower!" The fairy smiled and said, "Thank you, little flower. I will show you how to fly."

The fairy and the fairy talked and laughed together. They became best friends and shared everything together. They knew that the fairy had made them happy and that they could make new friends.
```

## final-greedy-6

Prompt: Two friends both wanted the same toy. They tried to find a fair way to share.

```text


One day, they found a big box in the garage. It was a big box with a lock on it. They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and found a key inside.

They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and found a key inside. They opened the box and
```

## final-sampled-6

Prompt: Two friends both wanted the same toy. They tried to find a fair way to share.

```text


One day, a big dog came. He was very strong. He wanted to play with the other kids. He wanted to play with them. He wanted to play with the other kids. He did not like the other kids. He did not like the other kids. He wanted the other kids.

The other kids wanted to play with the other kids. They wanted to play. They thought the other kids would not like the other kids. They wanted to be their friend. They wanted to make the same friends happy. They thought the other kids were nice.

They walked to the other kids. They asked them if they could play with the other kids. The kids said yes. They started to play. They gave the other kids a ball and a ball. They played with the other children and the other kids. They made them laugh. They had fun.
```

## final-greedy-7

Prompt: Noah found a mitten on the snowy path. He wanted to return it, but

```text
 he was too small to carry it. He tried to pull it off, but it was too heavy. He tried to pull it off, but it was too heavy.

He tried to pull it, but it was too heavy. He tried to pull it, but it was too heavy. He tried to pull it, but it was too heavy. He tried to pull it, but it was too heavy. He tried to pull it, but it was too heavy.

Then he had an idea. He said, "Let me help you, I can help you!" He pulled the rope and the rope, and the rope started to move. The rope was heavy and the rope was heavy. The rope was heavy and the rope was heavy.

The man was very happy. He thanked the rope and said, "You are a good friend, little one." He gave the rope to the rope and the rope. The rope was
```

## final-sampled-7

Prompt: Noah found a mitten on the snowy path. He wanted to return it, but

```text
 he was scared. He asked his mom if he could take it home.

His mom smiled and said, "Yes, you must take this mitten". She was very angry. She said, "No, it is mine now. You can't take it away by yourself. You don't have to be scared."

The mlf girl was angry. She said, "I want it back, mom. I want to go home. I want my mitten. I want it to go away."

His mom said, "No, you can't go outside. I don't want you to get hurt. You have to be careful. It's very dangerous. You need to go home. You have to go home now."

The girl felt sorry. She said, "But mom, I will not go in the hotel. I love you and I want to play with my mitten. It's not
```

## final-greedy-8

Prompt: The little boat had a hole in its side. Nora and her brother decided to

```text
 go on an adventure. They sailed and sailed until they reached the shore.

When they reached the shore, they saw many different animals. They were so happy to see them. They said hello and asked if they wanted to go on a boat.

The little boat said yes and they all went on their way. They had a lot of fun and were happy. They were friends forever.
```

## final-sampled-8

Prompt: The little boat had a hole in its side. Nora and her brother decided to

```text
 use the hole to take a hole out. They found a stick on the ground and put it on the hole. It worked!

Nora and her brother were so happy. They said goodbye to the boat and promised to never go on a big adventure in the pond.
```

## final-greedy-9

Prompt: At first, the kitten was afraid of the rain. Then it noticed

```text
 a big, scary monster. The monster was scared and ran away.

The kitten was very scared and ran away. The monster was very brave and he wanted to go back to the park. But the monster was too fast and the monster was too fast. The monster was very brave and he was never seen again.
```

## final-sampled-9

Prompt: At first, the kitten was afraid of the rain. Then it noticed

```text
 an amazing bird sitting in a tree. It was a beautiful bird on a branch.

The bird said to the bird, "Thank you! You are so kind." The bird replied, "You're welcome. I'm glad I could help."

The bird flew off with the bird and they flew across the clouds. They saw the bird again and started to sing. It sang a happy song as it flew away. The bird was so happy and said, "Thank you for teaching me how to sing!"

The bird smiled and said, "You're welcome!" From that day on, the bird flew every day and sang for her new friends. The bird was very happy and sang a happy song to sing.
```

## final-greedy-10

Prompt: Ben promised to water the flowers while his neighbor was away. On the last day,

```text
 Ben and his neighbor went to the park. Ben saw a big slide and wanted to go on it. He asked his neighbor, "Can I go on the slide, please?" His neighbor said, "No, you can't go on the slide. You can't go on the slide." Ben was sad, but he wanted to help his neighbor. He said, "I can help you. I can help you."

Ben was sad, but he was also happy to help his neighbor. He said, "I can help you. I can help you." He gave Ben a big hug and said, "Thank you, Ben. You are a good friend." Ben smiled and said, "You're welcome, Ben. I'm glad you like it. You are a good friend."

They went to the slide and had fun. Ben was happy. He said, "Thank you, Ben. You are a good friend." Ben
```

## final-sampled-10

Prompt: Ben promised to water the flowers while his neighbor was away. On the last day,

```text
 he told his family what happened. They all said they were very brave and had a lot of fun. From that day on, they always remembered to be kind and respectful to animals.
```

## final-greedy-11

Prompt: A girl made two paper crowns, one large and one small. She gave the small one to

```text
 the other, and the other one was very happy. She said, "Thank you, I love you!" The two friends laughed and played together all day.
```

## final-sampled-11

Prompt: A girl made two paper crowns, one large and one small. She gave the small one to

```text
 the other and said, "Eww!" The little girl was so happy that she took the flower home with her. 

The old one was very happy and thanked the little girl. She hugged the little girl and promised to never forget her special thing. The little one from then on, the little girl was no longer shy and happy. She knew that her big yellow crayon was special, and she could do a great job.
```

## final-greedy-12

Prompt: The lights went out just before the puppet show. The children found a way to

```text
 make the lights go up and down. They were so excited to see the lights.

The children clapped and cheered. They had made the lights go up and down. They were so happy to be together. They had made the lights go up and down. They were so proud of their work.
```

## final-sampled-12

Prompt: The lights went out just before the puppet show. The children found a way to

```text
 make the difference a goal. There it was a huge, black, purple cake! The children were so happy, and they clapped and cheered.

The children were so proud of the cake they did. They all clapped and cheered for the children. Everyone was so happy! The children were so happy, they wanted to make the cake together again.
```

## website-baseline-1

Prompt: Lily put her red ball in a blue box. Later, she opened the box and

```text
 saw a big, red ball. She wanted to play with it. She asked her mom if she could have it. Her mom said yes, but she had to be careful.

Lily took the red ball and threw it at the
```

## website-baseline-2

Prompt: Sam saw a small bird stuck in a puddle. He found a dry stick and

```text
 put it on the ground. He picked up the stick and put it in his pocket.

"Here, Sam, you can have this stick," said Sam. He took the stick and put it in his pocket. He gave it
```

## website-baseline-3

Prompt: Mia wanted to share her last apple with Ben. She cut it in two and

```text
 gave it to Ben.

"Here you go, Ben. You can have this. It is not a good one. It is a good one. It is very good at sharing."

Ben smiles and says, "Thank
```


## Provenance and raw-output digests

- lab: `7a517b2c065426748cd99702e82ea377877a7809`
- workshop: `e70d82b0c3262087ba5b1c546ebfd237f87a685d`
- harness: `b1c2efbd256eceeebdef7cf42b34165d01b8ccb6`
- Runtime image: `ghcr.io/supernovae/tiny-sparse-lab@sha256:e3356de49998903e5f03ee2cb28a9b33a5270d380d65d1ceb6fe195531ea812c`
- Final session-spec commit: `aa119230bbbca72d6d840ddf0e0e678b7cba49d0`
- CPU FP32 Linux/WSL2; Python3.14.4; Torch2.14.1+cpu.

| Native output file | SHA256 of original raw JSON |
|---|---|
| final-greedy-1.json | `b1587c8eef4ebf154e54382aa0d3d9767353211ef64ff102bab9c20cc167d5f8` |
| final-sampled-1.json | `ab941efe851f6b9f0910d60ef091c897072e62deb4f845a5e81f466126f2f01b` |
| final-greedy-2.json | `6c791ac48aeb0b448c7bafb873c01a4fe45ae728fe21ced1855bc790626cfb54` |
| final-sampled-2.json | `40ff9609aefd0560b049ecc3240779cfdecb654e4b73ceaadc3dc2eecc994bbb` |
| final-greedy-3.json | `4ac3c0af72aa8e53fcc4c732e9071ec3da4fb7feac7c1fb7f0b506eef51d76d7` |
| final-sampled-3.json | `c996b3d82914c4a6a3be2065f9f5375330f1c0ccc6a7776e99e3300b2c5e027e` |
| final-greedy-4.json | `b21057838f02f5b7974c75311b2e2e2dcb3c8df108c66d324cbfff580f90213f` |
| final-sampled-4.json | `42cfb59c2a05cb943c6033ff67e15e8ea3cacdb456952e3767131fea740a0f17` |
| final-greedy-5.json | `8a37cc65ba4f4c8b44f77b1920a1c80254c5a1f0c49f3a970fdb196d77d72bd7` |
| final-sampled-5.json | `74102d4fc2c4d8bd77fa691795a77d32cc7055f921b11b8e262c15944d9c2fbd` |
| final-greedy-6.json | `ff1c582fbc776df9e4ff90cdebba9478024d03a5ac8b2ff40751a3312fe4d13b` |
| final-sampled-6.json | `230fd0278d9d24d506c55b34ebfa3ffca81590f57ef42e2851b08365f92b9b73` |
| final-greedy-7.json | `89a3ff53a9c24e79288cfd2fcc1716f42ef03c8a73cec6947f8b55b0d6d49f50` |
| final-sampled-7.json | `3b20d5427da20b224dbf7bdcda09ae2d931d94decb805a82d9dcae8f4057c157` |
| final-greedy-8.json | `5343ae0d7b353c2f1e811ca00715236cdf42afc18fd9199054237a1c5a67b9cf` |
| final-sampled-8.json | `35f3dca619761bfeaaf741d9fc2196f6bd7771f6eaf142ad6b116c67e33b2fa9` |
| final-greedy-9.json | `dceaf63e92329e5e87e9ed9f60b3a39e6e77f8712f76d50a0759ad8fef7c0305` |
| final-sampled-9.json | `949bf496b81ebc46d35f2b5c541bfb5f546ca73d9e23fe9f7cd79697da4e3ca5` |
| final-greedy-10.json | `ac237da0df002e6fadfbe7d6ae77752b3ab013097a0e38c795624f3e73ab2d2f` |
| final-sampled-10.json | `57ef3d0423ce4a144e7d7adb3acc06189ccf67ce4537c9b228f367dd2ce1994d` |
| final-greedy-11.json | `6c0eb23c8d42ee4d7eb4cb770e039249ea0024e1baa29cce9d49838161b7c2c2` |
| final-sampled-11.json | `c3c2aeac05d6793952698da21565fd4f734cd7d9f25efd3ec9ad6458ab7e8f52` |
| final-greedy-12.json | `80d8a2986a3af460f827f9e763afe532d3985d219b6adfcc7e2dacccad09c011` |
| final-sampled-12.json | `30575dc231a92ad88270c24c8b393cdb0ec90299f6f47d85d6d9e7f17a2f66d6` |
| website-baseline-1.json | `798a41488c3de05491f75df0ab10bdbe7a53c85bcfacd43469ce543ed4327c90` |
| website-baseline-2.json | `82ececa3b9bb8cc2a818220459f6b77070987af999d46f7b4f688db8bb759d86` |
| website-baseline-3.json | `5f46e495708b41135b53e3c536c654272897591a21617cbfe886b6f9212c3496` |

The evidence package in this directory includes the resolved configuration, standalone evaluation metrics, full loss trajectory CSV, checkpoint closure index, and all 27 raw generation JSON outputs with local filesystem paths redacted to `${RUNS}`.
