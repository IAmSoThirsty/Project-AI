package com.projectai.evolution

import org.gradle.api.attributes.AttributeCompatibilityRule
import org.gradle.api.attributes.AttributeDisambiguationRule
import org.gradle.api.attributes.CompatibilityCheckDetails
import org.gradle.api.attributes.MultipleCandidatesDetails

abstract class BuildTypeCompatibilityRule : AttributeCompatibilityRule<String> {
    override fun execute(details: CompatibilityCheckDetails<String>) {
        val consumer = details.consumerValue
        val producer = details.producerValue

        if (consumer == null || producer == null || consumer == producer) {
            details.compatible()
            return
        }

        if (consumer == "release" && producer == "staging") {
            details.compatible()
        }
    }
}

abstract class BuildTypeDisambiguationRule : AttributeDisambiguationRule<String> {
    override fun execute(details: MultipleCandidatesDetails<String>) {
        val candidates = details.candidateValues.toSet()
        val consumer = details.consumerValue

        when {
            consumer != null && candidates.contains(consumer) -> details.closestMatch(consumer)
            candidates.contains("release") -> details.closestMatch("release")
            candidates.contains("debug") -> details.closestMatch("debug")
            candidates.isNotEmpty() -> details.closestMatch(candidates.sorted().first())
        }
    }
}

abstract class PlatformCompatibilityRule : AttributeCompatibilityRule<String> {
    override fun execute(details: CompatibilityCheckDetails<String>) {
        val consumer = details.consumerValue
        val producer = details.producerValue

        if (consumer == null || producer == null || consumer == producer) {
            details.compatible()
            return
        }

        if (consumer.startsWith("linux") && producer.startsWith("linux")) {
            details.compatible()
            return
        }

        if (consumer.startsWith("windows") && producer.startsWith("windows")) {
            details.compatible()
            return
        }

        if (consumer.startsWith("macos") && producer.startsWith("macos")) {
            details.compatible()
        }
    }
}

abstract class PlatformDisambiguationRule : AttributeDisambiguationRule<String> {
    override fun execute(details: MultipleCandidatesDetails<String>) {
        val candidates = details.candidateValues.toSet()
        val consumer = details.consumerValue

        when {
            consumer != null && candidates.contains(consumer) -> details.closestMatch(consumer)
            candidates.contains("linux-x64") -> details.closestMatch("linux-x64")
            candidates.contains("windows-x64") -> details.closestMatch("windows-x64")
            candidates.contains("macos-arm64") -> details.closestMatch("macos-arm64")
            candidates.isNotEmpty() -> details.closestMatch(candidates.sorted().first())
        }
    }
}
