# CoLoSSI: Multi-Robot Task Allocation in Spatially-Distributed and Communication Restricted Environments

Welcome to the **CoLoSSI** project repository! This repository contains the implementation and simulation scripts for the CoLoSSI algorithm, designed for efficient multi-robot task allocation in spatially-distributed and communication-restricted environments.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)

## Introduction

The CoLoSSI algorithm addresses the challenge of coordinating heterogeneous multi-robot systems for missions involving spatially localized tasks. Unlike traditional task allocation methods that assume atomic task completion, CoLoSSI employs a non-atomic model, allowing tasks to be completed incrementally by multiple robots over time. This repository includes various implementations and simulation scripts to demonstrate the efficacy of the CoLoSSI algorithm and its variants.

## Features

- **Non-Atomic Task Model**: Allows tasks to be partially completed over separate intervals, facilitating cooperation among robots.
- **Sequential Single-Item Auctions**: Employs a load-balancing approach to ensure efficient task distribution with reduced computational complexity.
- **Distributed Variant**: Adapts to communication-restricted scenarios, enabling robust task allocation despite sparse network connectivity.
- **Adaptive Replanning**: Continuously adapts mission plans based on new information, enhancing overall mission success.
- **Connectivity-Aware Algorithm**: Optimizes networking conditions, promoting better inter-robot communication and coordination.

## Installation

Clone the repository to your local machine using:

```bash
git clone https://github.com/yourusername/CoLoSSI.git
cd CoLoSSI
