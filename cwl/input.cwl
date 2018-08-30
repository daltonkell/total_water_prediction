#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  atmospheric:
    type: string
  ocean:
    type: string
  river:
    type: string
