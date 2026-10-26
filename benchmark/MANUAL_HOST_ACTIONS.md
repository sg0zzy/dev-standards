# Separately controlled host experiments

This file documents actions an operator may need later. The implementation has no
administrative mode and performs none of these actions. This standards task does
not authorize executing them. Keep the headless server's recovery path available.

## BIOS UMA states

The suite's profile names label expected observed VRAM; they do not select BIOS
settings. Establish each state independently using vendor-supported procedures,
then verify BIOS index, physical VRAM/GTT, MemTotal, TTM limits and the engine's
actual settings with `check` before starting inference.

The reported current index **8 = 96 GiB** is absent from the advertised sysfs list
**0 through 7**. Do not assume it is safe to write 8 back, or that choosing another
index can be reversed remotely. Before considering a later change, independently
verify a supported route back to 96 GiB, out-of-band/local access and a recovery
plan. No firmware-attribute writes or reboot commands are provided here.

Record whether the 64 GiB and 512 MiB states require boot/driver/TTM changes.
The supplied `ttm.pages_limit=4061515` is approximately 15.5 GiB at 4096-byte pages;
it is not evidence that a 512 MiB UMA state can dynamically allocate the model's
roughly 68 GiB working set. A small carve-out without adequate GTT may fail.
Any later host tuning is a separately authorized experiment; record the exact
command line and preserve all other settings. The suite never grows GTT or
reduces expert cache automatically.

## Genuinely cold filesystem cache

A fresh process alone does not empty Linux's page cache. Repeated process starts
measure a warm filesystem once weights have been read. Hashing the model also
warms it. Prepare the hash manifest and fixtures well before a cold trial.

A genuinely cold trial may require a separately scheduled reboot, or a privileged
administrator clearing the filesystem cache. Either can disrupt this headless
host and unrelated services. The operator must choose and perform any such
action outside the utility, under separate explicit authorization and with an
appropriate recovery path. No `drop_caches`, swap-clearing or reboot command is
included. Avoid unrelated readers and record the method, timing and evidence.
It is also valid to omit this trial and report that cold-filesystem performance
is unknown.

After independently establishing the intended state, select the observer's
explicit optional `--condition manual-cold-fs` mode. Its confirmation warns that
the state is operator-attested; it does not clear caches, verify all pages are
cold, disable swap, or require root. Compare with `cold-process-warm-fs` using the
same files and engine settings. Keep load costs separate from inference timing.

## Process lifetime, memory pressure and ports

Do not stop the existing production/development Strata instance for this task.
For later fresh-process tests, the operator must arrange an appropriate idle
maintenance window or a separate instance with a free port and sufficient
**combined** CPU/GPU/OS memory headroom. The current engine already occupies much
of the unified pool. A free port does not imply enough memory.

Use a verified normal startup mechanism. Inspect whether that mechanism itself
terminates other engines: the inspected upstream server contains leftover-engine
cleanup, so launching another server is not automatically harmless. This suite
supplies no generic launcher and cannot make an unknown startup script safe.

Start `watch-load` first with a nonexistent, unique PID-file path. In the normal
launch configuration, avoid loading another model on an already occupied device.
Publish only the actual new engine PID to that PID file after it exists. The
observer validates its executable but cannot independently map HTTP to a PID
if several engines share the same executable. Ensure that mapping yourself.
For an unambiguous load baseline, set the observer configuration's `engine_pid`
to null until the new PID is published; early process metrics then remain null.
A process may stay running when the observer exits; lifecycle remains entirely
under operator control.

Record all unavoidable background work and repeat configurations in a balanced
order if feasible, without discarding unfavorable repetitions. Do not silently
change power limits, optimizations, context, KV, MTP or expert slots between
trials. Export logs for inspection before sharing any results.
