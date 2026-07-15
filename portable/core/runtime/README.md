# PETP Background Runtime

This folder contains the no-GUI runtime for PETP.

## Files

- `BackgroundRuntime.py`: run execution/pipeline without wx UI.
- `UiProcessorPolicy.py`: policy for GUI-bound processors in no-GUI mode.

## Skip behavior

In no-GUI mode, GUI processors are handled by policy:

- `skip` (default): log and continue.
- `abort`: stop execution and return error.

Current GUI processor types:

- `SHOW_RESULT`
- `INPUT_DIALOG`
- `MATPLOTLIB`


