"""
Cybersecurity educational content: Digital Threats, Attack Vectors, and Defense.

This module provides structured educational content about cybersecurity,
covering malware, exploitation techniques, web-based attacks, and defensive strategies.
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class CybersecurityKnowledge:
    """Manages cybersecurity educational content and integrates with knowledge base."""

    def __init__(self, data_dir: str = "data"):
        """Initialize cybersecurity knowledge module."""
        self.data_dir = data_dir
        self.knowledge_file = os.path.join(data_dir, "cybersecurity_knowledge.json")
        self.content = self._get_structured_content()

    def _get_structured_content(self) -> dict[str, Any]:
        """Return the complete structured cybersecurity knowledge base."""
        return {
            "title": "An Anatomy of Digital Threats: Attack Vectors, Exploitation, and Defensive Countermeasures",
            "introduction": {
                "overview": (
                    "In the digital realm, a company's web servers are often the equivalent of its public shop window. "
                    "They are the primary interface for advertising, exhibiting information, and conducting business. "
                    "However, these servers are complex programs with a high probability of containing bugs and vulnerabilities. "
                    "Just as one would not leave a shop window open for any passerby to reach in and take what they want, "
                    "it is strategically critical to protect these digital assets from being shattered by attackers seeking "
                    "to exploit them for unauthorized access to sensitive data."
                ),
                "scope": (
                    "This document provides a comprehensive analysis of the modern digital threat landscape, "
                    "examining a spectrum of attacks from historical viruses to sophisticated, multi-vector campaigns. "
                    "We will dissect the orchestration of these attacks—exploring how systems can go wrong—and detail "
                    "the essential defensive countermeasures required to ensure they do not."
                ),
                "topics": [
                    "Malware: An examination of self-replicating and malicious software",
                    "System Exploitation: Technical breakdown of software vulnerabilities",
                    "Web-Based Attacks: Methods used to reconnoiter and attack web applications",
                    "Proactive Defense Frameworks: Strategic overview of security policies and procedures",
                ],
            },
            "malware": {
                "strategic_importance": (
                    "Understanding the nature of malware is a cornerstone of cybersecurity. "
                    "Despite being one of the oldest forms of digital threat, malware—encompassing viruses, worms, "
                    "and trojans—continues to evolve. Modern variants leverage sophisticated techniques to infect systems, "
                    "propagate across networks, and evade detection, making them a persistent and dynamic challenge for defenders."
                ),
                "virus_lifecycle": {
                    "infection_phase": (
                        "During this stage, the virus seeks to propagate itself to other files or systems. "
                        "Virus writers must strike a delicate balance between spreading the infection rapidly and remaining undetected. "
                        "The infection process may not be immediate, employing various triggers and strategies to avoid raising suspicion."
                    ),
                    "attack_phase": (
                        "This phase involves the execution of the virus's primary payload, which can range from "
                        "displaying a simple message on the screen to corrupting data or overwriting critical system sectors."
                    ),
                },
                "categories": {
                    "concealment_techniques": {
                        "stealth_viruses": (
                            "These viruses actively hide their presence by intercepting system calls to show an uninfected version "
                            "of a file or sector. For example, the historic Brain virus would intercept any attempt to view an infected "
                            "boot sector and return an image of the original, clean sector instead."
                        ),
                        "polymorphic_viruses": (
                            "To evade signature-based scanners, these viruses mutate their code, creating a different version of themselves "
                            "with each new infection. The Whale virus, for instance, was known to create 33 different versions of itself as it spread."
                        ),
                        "armored_viruses": "A category of viruses designed to resist analysis by security researchers.",
                        "camouflage_viruses": "These viruses attempt to appear as benign programs to scanners.",
                        "tunneling_viruses": (
                            "This type of virus attempts to bypass anti-virus monitors by following interrupt chains down to "
                            "the basic DOS or BIOS interrupt handlers before installing itself."
                        ),
                    },
                    "infection_strategies": {
                        "fast_infectors": (
                            "A fast infector will infect any file that is accessed, spreading rapidly but with higher visibility."
                        ),
                        "slow_infectors": (
                            "These limit activity to only infecting files as they are created or modified to reduce visibility."
                        ),
                        "sparse_infectors": "A category of virus that infects files only occasionally.",
                        "multipartite_viruses": (
                            "A category of virus that can infect multiple parts of a system, such as boot sectors and executable files."
                        ),
                        "cavity_viruses": (
                            "Also known as spacefiller viruses, these attempt to install themselves in the empty sections of a file."
                        ),
                    },
                    "specialized_vectors": {
                        "batch_file_viruses": (
                            "These viruses use simple batch files to transmit executable code, which can either be a virus itself "
                            "or a 'dropper' program that installs a virus."
                        ),
                        "ntfs_ads_viruses": (
                            "These viruses exploit the Alternate Data Streams (ADS) feature of the NT File System to hide their components."
                        ),
                        "macro_viruses": (
                            "Propagating through applications that support macros (e.g., Microsoft Word), "
                            "these viruses require a host document to spread from one system to another."
                        ),
                    },
                },
                "case_study_love_letter": {
                    "name": "ILOVEYOU (Love Letter) Worm",
                    "year": 2000,
                    "description": (
                        "The Love Letter worm is a classic case study in social engineering and malware propagation. "
                        "It arrived as an email with the subject line 'ILOVEYOU' and an attachment named LOVE-LETTER-FOR-YOU.TXT.vbs. "
                        "The double extension was designed to trick users into thinking it was a harmless text file, "
                        "but it was in fact a Visual Basic Script that executed when opened."
                    ),
                    "payload": {
                        "propagation": (
                            "It sent a copy of itself to every entry in the victim's Microsoft Outlook address book, rapidly amplifying its reach."
                        ),
                        "file_overwriting": (
                            "It searched all local and networked drives for files with script and web-related extensions "
                            "(VBS, JS, CSS, WSH, HTA, etc.) and overwrote them with its own code. It also overwrote JPG and JPEG image files."
                        ),
                        "file_hiding": (
                            "It located multimedia files with MP2 or MP3 extensions, marked them as hidden, and then created a new, "
                            "visible file with the same name but a .VBS extension, containing the worm's code."
                        ),
                    },
                    "lesson": (
                        "The success of the Love Letter worm demonstrates how easily human curiosity can be weaponized, "
                        "hinging on its ability to exploit both technical vulnerabilities and predictable human behavior."
                    ),
                },
            },
            "system_exploitation": {
                "overview": (
                    "Beyond self-contained malware that tricks users into execution, attackers also exploit fundamental vulnerabilities "
                    "in how software is designed and how programs manage memory. These exploits target the root causes of software insecurity, "
                    "often residing deep within a program's handling of data and execution flow."
                ),
                "strategic_importance": (
                    "Understanding these low-level techniques is strategically vital for developing resilient software that is secure by design. "
                    "Mastering these fundamentals is non-negotiable for any organization serious about proactive defense engineering."
                ),
                "memory_and_execution": {
                    "architecture": (
                        "On modern Intel-based (x86) systems, programs operate within 32-bit addressable Random Access Memory (RAM). "
                        "This memory is volatile, meaning its contents are lost when the system powers down. "
                        "When a program runs, its instructions and data are loaded into RAM, and its execution state is managed on the stack."
                    ),
                    "buffer_overflow": (
                        "A classic buffer overflow attack exploits this architecture. It occurs when a program attempts to write more data "
                        "into a fixed-length buffer than it can hold. A vulnerable C function like strcpy, which does not perform bounds checking, "
                        "can be used to write a malicious string that overflows the buffer and overwrites adjacent memory on the stack. "
                        "A primary target for this overwrite is the saved instruction pointer (eip), which stores the address of the next instruction "
                        "the program should execute. By overwriting the eip with the address of their own code, an attacker can hijack the program's "
                        "control flow and redirect it to execute malicious instructions."
                    ),
                },
                "shellcode": {
                    "definition": (
                        "The arbitrary code executed after a successful exploit is known as shellcode. "
                        "The term originates from the common practice of using this code to gain shell access "
                        "(a command-line interface) on the compromised system."
                    ),
                    "types": {
                        "port_binding": {
                            "mechanism": (
                                "The shellcode creates a new listening socket on a specific port of the target machine "
                                "and waits for the attacker to connect to it."
                            ),
                            "requirements": (
                                "The target's network must permit an inbound connection from the attacker to the port opened by the shellcode. "
                                "This is often blocked by firewalls."
                            ),
                        },
                        "reverse_connect": {
                            "mechanism": (
                                "After exploitation, the shellcode instructs the target machine to initiate a connection back "
                                "to a listening port on the attacker's machine."
                            ),
                            "requirements": (
                                "The target's network must permit outbound connections. This is highly effective against targets behind firewalls "
                                "that block inbound traffic but allow outbound traffic."
                            ),
                        },
                        "find_socket": {
                            "mechanism": (
                                "Instead of creating a new connection, this shellcode enumerates the existing file descriptors "
                                "on the compromised application to find the socket already connected to the attacker."
                            ),
                            "requirements": (
                                "The initial exploit connection must remain open. This method avoids creating new network traffic, "
                                "making it stealthier and capable of bypassing certain network defenses."
                            ),
                        },
                    },
                },
                "format_string_vulnerabilities": {
                    "description": (
                        "Another critical class of vulnerability arises from the improper use of formatting functions like printf() in C. "
                        "These functions are designed to print formatted output based on a format string containing special tokens "
                        "(e.g., %s for string, %d for decimal)."
                    ),
                    "secure_form": 'printf("<format string>", <variables>);',
                    "insecure_form": "printf(<user supplied string>);",
                    "exploitation": (
                        "When an attacker can supply the format string itself, they gain powerful control over the program's behavior. "
                        "This vulnerability allows an attacker to both read from arbitrary memory locations (by using tokens like %x to print values "
                        "from the stack) and, more dangerously, write to arbitrary memory locations. The %n format token, for instance, writes the number "
                        "of bytes printed so far into a memory address specified on the stack. An attacker can leverage this to overwrite critical program data, "
                        "function pointers, or other control structures, leading to arbitrary code execution."
                    ),
                },
            },
            "web_attacks": {
                "strategic_importance": (
                    "The strategic importance of web application security cannot be overstated, as these platforms are the public face "
                    "of modern organizations. The majority of web application vulnerabilities stem not from bugs in the programming languages themselves, "
                    "but from fundamental failures in development practices and server configuration. Improper data validation remains a primary root cause."
                ),
                "attacker_methodology": {
                    "reconnaissance": {
                        "description": (
                            "A systematic web penetration test begins with reconnaissance—the process of gathering information about a target."
                        ),
                        "icmp_sweeps": (
                            "Attackers use tools like fping to perform ICMP sweeps, identifying live hosts across a network range."
                        ),
                        "dns_reconnaissance": (
                            "This is often followed by DNS reconnaissance to map domain names to IP addresses, "
                            "helping to identify high-value targets like web servers and mail servers."
                        ),
                    },
                    "scanning": {
                        "description": (
                            "Once targets are identified, attackers employ automated web vulnerability scanners to probe for common weaknesses."
                        ),
                        "nikto": {
                            "description": (
                                "This scanner provides comprehensive reports on web server configurations. "
                                "It identifies the server version, detects outdated software (e.g., Apache, PHP), "
                                "and enumerates allowed HTTP methods that could be insecure (PUT, DELETE, TRACE). "
                                "It can also discover misconfigurations such as directory indexing, which exposes file and directory listings to the public."
                            ),
                        },
                        "skipfish": {
                            "description": (
                                "This tool conducts a recursive crawl of a target website to prepare an interactive sitemap. "
                                "It then uses dictionary-based probes to test for a wide range of security vulnerabilities, "
                                "providing a detailed map of potential issues throughout the application."
                            ),
                        },
                    },
                },
                "proxy_exploitation": {
                    "description": (
                        "An HTTP proxy serves as a 'middleman' in web transactions, intercepting and logging all connections "
                        "between a web client (browser) and a web server. While proxies can be used defensively to filter connections, "
                        "they are also powerful tools for attackers."
                    ),
                    "burp_suite": (
                        "Proxy tools like Burp Suite allow a penetration tester to intercept, inspect, and manipulate HTTP requests in real-time. "
                        "By altering data in a request before it reaches the server, an attacker can test how the application responds to unexpected "
                        "or malicious input. This technique is invaluable for manually identifying and exploiting complex vulnerabilities such as "
                        "cross-site scripting (XSS) and SQL injection, where automated scanners may fail. "
                        "The ability to modify requests on the fly provides deep insight into the application's logic and data validation flaws."
                    ),
                },
            },
            "proactive_defense": {
                "overview": (
                    "A formal security framework is the backbone of a defensible enterprise, transforming reactive incident response "
                    "into a proactive, risk-aligned security program. Defending against modern threats is not a one-time fix but a continuous cycle "
                    "of discovery, assessment, and remediation."
                ),
                "four_pillars": {
                    "discovery": "This initial phase focuses on mapping the network architecture and identifying potential targets and services.",
                    "assessment": "In this stage, the identified targets are audited to enumerate system-level and network vulnerabilities.",
                    "secure": "The findings from the assessment are evaluated, and this information is used to educate technical staff on the identified risks.",
                    "remediate": "The final stage involves locking down targets and applying the necessary fixes to mitigate the discovered vulnerabilities.",
                },
                "core_policies": {
                    "patch_management": (
                        "This program reduces risk by ensuring that systems are not running software with known, exploitable vulnerabilities. "
                        "Guidelines such as those in NIST SP 800-40 provide a foundation for developing effective patch management policies."
                    ),
                    "change_control": (
                        "A strong change control process mitigates vulnerabilities caused by human error and system misconfigurations, "
                        "ensuring that all modifications to production systems are reviewed and approved."
                    ),
                    "multifactor_access_control": (
                        "This strengthens authentication beyond simple passwords by requiring at least two forms of verification "
                        "and limits administrative access to only authorized individuals."
                    ),
                    "critical_system_isolation": (
                        "This involves isolating critical systems from the general network using whitelists, "
                        "Access Control Lists (ACLs), and VLANs to limit an attacker's ability to move laterally after an initial compromise."
                    ),
                },
                "vulnerability_disclosure": {
                    "cert_role": (
                        "The CERT Coordination Center (CERT/CC) serves as a central body for coordinated disclosure, "
                        "facilitating communication between security researchers who discover vulnerabilities and the vendors responsible for patching them."
                    ),
                    "tension": (
                        "A common point of friction exists regarding the timeline for implementing fixes. "
                        "Vendors often prefer to integrate patches into their regularly scheduled release cycles to manage costs and complexity. "
                        "In contrast, researchers and security advocates often argue for more immediate action to prevent customers from being exposed "
                        "to unnecessary risk. This tension highlights the ongoing challenge of balancing business practicalities with immediate security needs."
                    ),
                },
            },
            "secure_implementation": {
                "overview": (
                    "A secure strategic framework is only as strong as its technical foundation. "
                    "Robust security relies on diligent implementation at both the code and system levels."
                ),
                "data_integrity": {
                    "integrity_checking": (
                        "This defensive measure works by recording cryptographic signatures of system files and critical sectors. "
                        "This baseline can be compared against the current state of the system at a later time to detect any unauthorized changes. "
                        "In the event of a malware infection, an integrity checker provides the only reliable way to discover exactly what damage a virus has done."
                    ),
                    "backups": (
                        "Maintaining a reliable and up-to-date backup is the most critical defense against data loss. "
                        "Recovery tools do not always restore perfect copies of original files after a hardware failure or malware attack. "
                        "An active, pre-disaster backup strategy is the best and often only way to ensure a full recovery."
                    ),
                },
                "secure_coding": {
                    "input_validation": (
                        "Developers must assume all user input is potentially malicious and properly validate incoming data. "
                        "For example, if a form field requests a zip code and the user enters 'abcde,' "
                        "the application should handle this gracefully without failing or opening an avenue for exploitation."
                    ),
                    "exception_handling": (
                        "Code that might raise an error, such as file operations or network requests, should be wrapped in exception handling blocks "
                        "(e.g., try/except in Python or try/catch in .NET). This prevents unexpected crashes that could leak sensitive information "
                        "or leave the system in an insecure state."
                    ),
                },
            },
        }

    def get_all_content(self) -> dict[str, Any]:
        """Get the complete cybersecurity knowledge base."""
        return self.content

    def get_section(self, section: str) -> dict[str, Any] | None:
        """
        Get a specific section of the knowledge base.

        Args:
            section: One of 'introduction', 'malware', 'system_exploitation',
                    'web_attacks', 'proactive_defense', 'secure_implementation'
        """
        return self.content.get(section)

    def get_subsection(self, section: str, subsection: str) -> Any:
        """Get a specific subsection within a section."""
        section_data = self.get_section(section)
        if section_data:
            return section_data.get(subsection)
        return None

    def search_content(self, keyword: str) -> list[dict[str, str]]:
        """
        Search for a keyword across all content.

        Returns a list of matches with section and context.
        """
        results = []
        keyword_lower = keyword.lower()

        def search_recursive(data: Any, path: str = "") -> None:
            """Recursively search through nested dictionaries and lists."""
            if isinstance(data, dict):
                for key, value in data.items():
                    new_path = f"{path}.{key}" if path else key
                    if isinstance(value, str) and keyword_lower in value.lower():
                        results.append(
                            {
                                "path": new_path,
                                "content": (
                                    value[:200] + "..." if len(value) > 200 else value
                                ),
                            }
                        )
                    search_recursive(value, new_path)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    search_recursive(item, f"{path}[{i}]")

        search_recursive(self.content)
        return results

    def export_to_json(self, filepath: str | None = None) -> str:
        """
        Export the complete knowledge base to a JSON file.

        Args:
            filepath: Optional custom filepath. If None, uses default location.

        Returns:
            The filepath where the content was saved.
        """
        if filepath is None:
            filepath = self.knowledge_file

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.content, f, indent=2, ensure_ascii=False)
            logger.info(f"Cybersecurity knowledge exported to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error exporting cybersecurity knowledge: {e}")
            raise

    def integrate_with_memory_system(self, memory_system: Any) -> None:
        """
        Integrate cybersecurity knowledge with the MemoryExpansionSystem.

        Args:
            memory_system: Instance of MemoryExpansionSystem
        """
        try:
            # Add each major section as a category in the knowledge base
            sections = [
                "introduction",
                "malware",
                "system_exploitation",
                "web_attacks",
                "proactive_defense",
                "secure_implementation",
            ]

            for section in sections:
                section_data = self.get_section(section)
                if section_data:
                    memory_system.add_knowledge(
                        category="cybersecurity_education",
                        key=section,
                        value=section_data,
                    )
                    logger.info(f"Added cybersecurity section: {section}")

            # Add the title and metadata
            memory_system.add_knowledge(
                category="cybersecurity_education",
                key="title",
                value=self.content["title"],
            )

            logger.info(
                "Successfully integrated cybersecurity knowledge with memory system"
            )
        except Exception as e:
            logger.error(f"Error integrating cybersecurity knowledge: {e}")
            raise

    def get_summary(self) -> str:
        """Get a brief summary of available content."""
        summary = f"# {self.content['title']}\n\n"
        summary += "## Available Sections:\n\n"
        summary += "1. **Introduction**: Modern threat landscape overview\n"
        summary += "2. **Malware**: Viruses, worms, trojans, and case studies\n"
        summary += "3. **System Exploitation**: Buffer overflows, shellcode, format string vulnerabilities\n"
        summary += (
            "4. **Web Attacks**: Reconnaissance, scanning, and proxy exploitation\n"
        )
        summary += "5. **Proactive Defense**: Security frameworks and policies\n"
        summary += (
            "6. **Secure Implementation**: Data integrity and secure coding practices\n"
        )
        return summary
