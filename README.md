# FlexBuddy — Intelligent AI-Powered Team Formation & Workforce Matching

> An intelligent workforce management system that matches employees to projects, forms complementary teams, balances workload, detects skill gaps, and recommends internal talent or recruitment needs.

## 🚀 Overview

**FlexBuddy** is an AI-assisted workforce management and team formation platform designed to help organizations assign the right employees to the right projects.

Instead of selecting employees only based on their skill similarity, FlexBuddy considers multiple factors such as:

- Technical skill proficiency
- Skill importance for the project
- Employee availability
- Current workload
- Employee interests
- Location compatibility
- Team skill coverage
- Skill gaps
- Internal talent availability
- Recruitment requirements

The system first determines whether an employee is **eligible** for a project and then calculates an **explainable match score**.

FlexBuddy also goes beyond individual employee matching by forming **complementary teams**. If an important skill is missing from the selected team, the system searches the internal workforce first. If the required capability is not available internally, FlexBuddy generates a **recruitment recommendation**.

---

## 🎯 Problem Statement

Traditional employee allocation systems often rely on:

- Manual employee selection
- Basic skill filtering
- Availability alone
- Manager experience
- Simple keyword matching

This can result in:

- Poor skill coverage
- Overloaded employees
- Duplicate skill sets within a team
- Important skill gaps
- Underutilized employees
- Unnecessary external hiring

For example, selecting the three employees with the highest Python scores does not necessarily produce the best team.

A better team could contain:

text
Employee 1 → Python + NLP
Employee 2 → React + SQL
Employee 3 → AWS + DevOps



                    ┌──────────────────────┐
                    │     TEAM LEAD        │
                    │ Creates a Project    │
                    └──────────┬───────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │  PROJECT DESCRIPTION    │
                  │                         │
                  │ "Build an AI chatbot    │
                  │ using Python, NLP,      │
                  │ FastAPI and AWS..."     │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │      AI / NLP LAYER     │
                  │                         │
                  │ Extract requirements    │
                  │ Extract skills           │
                  │ Identify project phase   │
                  │ Identify importance      │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │ STRUCTURED REQUIREMENTS │
                  │                         │
                  │ Python → 4/5            │
                  │ NLP → 4/5               │
                  │ FastAPI → 3/5           │
                  │ SQL → 3/5               │
                  │ AWS → 3/5               │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │ EMPLOYEE DATABASE       │
                  │                         │
                  │ Skills                  │
                  │ Proficiency              │
                  │ Availability             │
                  │ Workload                 │
                  │ Interests                │
                  │ Location                 │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │ RULE-BASED ELIGIBILITY │
                  │                         │
                  │ Critical Skills?        │
                  │ Minimum proficiency?    │
                  │ Enough capacity?        │
                  │ Location compatible?    │
                  └────────────┬────────────┘
                               │
                    ┌──────────┴───────────┐
                    │                      │
                    ▼                      ▼
               NOT ELIGIBLE             ELIGIBLE
                                          │
                                          ▼
                              ┌─────────────────────┐
                              │ MATCH SCORE ENGINE  │
                              │                     │
                              │ Skill Match  60%   │
                              │ Availability 15%   │
                              │ Interest     10%   │
                              │ Location      5%   │
                              │ Capacity     10%   │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │ CANDIDATE RANKING   │
                              │                     │
                              │ Arun      → 94%    │
                              │ Priya     → 87%    │
                              │ Vishnu    → 82%    │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │ TEAM FORMATION      │
                              │                     │
                              │ Maximize coverage  │
                              │ Avoid duplication   │
                              │ Balance workload    │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │ TEAM HEALTH CHECK   │
                              │                     │
                              │ Skill Coverage     │
                              │ Workload Balance    │
                              │ Availability        │
                              │ Compatibility       │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │ SKILL GAP ANALYSIS  │
                              │                     │
                              │ Required Skills     │
                              │       -             │
                              │ Team Skills         │
                              │       =             │
                              │ Missing Skills      │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │ INTERNAL TALENT     │
                              │ SEARCH              │
                              └──────────┬──────────┘
                                         │
                            ┌────────────┴────────────┐
                            │                         │
                            ▼                         ▼
                     TALENT FOUND              NOT FOUND
                            │                         │
                            ▼                         ▼
                  INTERNAL ALLOCATION          RECRUITMENT
                  RECOMMENDATION               RECOMMENDATION
                            │                         │
                            └────────────┬────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │ WORKFORCE INSIGHT   │
                              │                     │
                              │ Final Team          │
                              │ Team Health         │
                              │ Skill Gaps          │
                              │ Internal Talent     │
                              │ Hiring Needs        │
                              └─────────────────────┘
