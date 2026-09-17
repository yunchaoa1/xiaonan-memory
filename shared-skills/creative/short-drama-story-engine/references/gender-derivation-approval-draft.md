# Gender Derivation Approval-Draft Workflow

Use this when the `Gender Derivation for Animal-Ensemble Roles` section in SKILL.md
applies, and you are actually deriving gender for an ensemble role one character at a
time. It captures the concrete cadence that worked in practice and the reusable
approval-draft format.

> **Correction from 2026-08-13 (user-caught, read before using the old tiebreaker):**
> the original tiebreaker "one version gains an extra layer → lock it" is a trap.
> In male-dominated fields the female version *always* gains an extra discrimination
> layer, so applying it blindly flipped every traditional role (牛、猴) to female — the
> exact anti-stereotype reversal the user rejects. Final lockout for 鼠/牛/猴 was
> **鼠女、牛女、猴男** — 猴 was reversed to male after the user called it out, because its
> plot debt (技术债 / 被当万能补丁 / 聪明不被信任) runs entirely on the 猴 character's
> personality and needs no gender reversal. Apply the baseline-first rule from SKILL.md
> (`顺应刻板印象` default, reverse only on non-reversible plot need) instead of
> "whichever version is sharper".

## The core derivation move: write both versions out

Do not reason about "male vs female" in the abstract and then announce a conclusion.
For each role, write out **two concrete推演 blocks side by side**:

1. **女版推演** — how this specific workplace conflict lands if the role is female:
   what power relationship changes, how the same visible action gets re-read, what extra
   accusation/humiliation/retaliation appears, how the emotional debt deepens.
2. **男版推演** — the same, honestly: which parts still work, and then the decisive test.

Then apply the tiebreaker — **with the baseline-first correction**:

> Start from the audience stereotype (`顺应刻板印象`): traditional roles default male,
> relationship/service roles default female. Reverse only when the plot has a
> *non-reversible* strong need. Do **not** lock "whichever version gains an extra
> humiliation/credit-theft/burden-shifting layer" — in male-dominated fields the female
> version always gains that layer, so this test mechanically flips every traditional role
> female (the bug that produced 牛女、猴女 before the user corrected it). A version that
> only re-words the accusation (男版 "滑头/不够担当" vs 女版 "私下经营关系") is a sign the
> gender is NOT carrying real causal weight — leave it at baseline, don't reverse.

Where the baseline-first test landed for the first three roles:

- **鼠 → 女 (kept):** customer/service work is a relationship-type role where the female
  stereotype is the natural baseline, and the devaluation ("会哄客户 / 把客户处成私人关系")
  is a real phenomenon rather than a forced reversal.
- **牛 → 女 (locked, user said leave it):** originally derived female via the trap; the user
  accepted the lockout and ordered "第二集已经定了不要动". Do not treat this as a pattern —
  it is a one-off that slipped through before the correction.
- **猴 → 男 (reversed after correction):** technician/tool-builder is a traditional role;
  its plot debt runs on the 猴 character's "跳/试/不留痕" personality and needs no gender
  reversal, so it defaults male.

## Approval-draft structure (one file per character)

Create `第一季首批五人_性别剧情推导审阅稿_v0.1_<角色>.md` with this fixed skeleton:

1. **状态** header — explicit "只供凡哥审方向，未锁性别，未回写第N集".
2. **当前不能动的剧情骨架** — restate the role's locked处境、情绪债、第一动作 from the
   approved source file. Do not silently change established causality.
3. **女版推演** — concrete consequences of the female reading.
4. **男版推演** — the honest counterfactual, including "能成立的部分" and "不够尖锐的部分".
5. **暂定建议 / 最终决定** — recommend, then wait.
6. **动物与文化校验** — last, explicitly "不参与定性别", only checks compatibility.
7. **若通过，回写第N集时只改三处** — a closed list of exactly what changes if approved
   (e.g. 鼠: ①劳动被贬为"维护客户" ②指控落到"私下关系" ③明确她独自圆场面的动机).

## Cadence rules

- **One character at a time.** Do not batch-derive all five/six/twelve in one draft. Present
  鼠, wait for approval, then 牛, then 猴. Each approval is a separate user gate.
- **Approval → lock → revise → next.** When the user says "可以/继续": mark the approval draft
  "✅ 凡哥已确认" and change "暂定建议" to "最终决定"; update the source file's pronouns
  (它→她/他) for that role; revise the episode's **listed three places only** (or deliver the
  episode 动作链/正文 if it doesn't exist yet); then start the next character's draft.
- **Same-gender run is a red flag to check, not proof of correctness.** If several
  consecutive characters derive to the same gender, stop and test BOTH directions: it may
  be a natural per-plot result, or it may be the "sharper-version" trap silently flipping
  every male-dominated role female (this happened with 鼠/牛/猴). Reset to the stereotype
  baseline and re-derive the traditional-role characters. Do not force a different gender
  merely to break the run either — that is quota-thinking in reverse.
- **Never silently overwrite.** After approval, revise the specific episode; do not rewrite
  unrelated characters or the season causality. The derivation only unlocks gender + the
  listed three revisions.
