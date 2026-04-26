using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace ProjectAI.VR.Autonomy
{
    /// <summary>
    /// Classifies natural language requests into RequestType categories
    /// Uses keyword matching and linguistic patterns
    /// </summary>
    public class RequestClassifier
    {
        // Keywords that suggest commands
        private static readonly HashSet<string> CommandIndicators = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "turn", "set", "change", "activate", "deactivate", "enable", "disable",
            "start", "stop", "open", "close", "show", "hide", "move", "rotate",
            "delete", "remove", "add", "create", "execute", "run", "do"
        };

        // Keywords that suggest polite requests
        private static readonly HashSet<string> RequestIndicators = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "please", "could you", "would you", "can you", "will you",
            "might you", "may i", "could i", "would it be possible"
        };

        // Keywords that suggest suggestions
        private static readonly HashSet<string> SuggestionIndicators = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "maybe", "perhaps", "possibly", "what if", "how about",
            "might be good", "we could", "consider", "think about", "suggest"
        };

        // Keywords that suggest casual conversation
        private static readonly HashSet<string> CasualIndicators = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "is", "are", "was", "were", "it's", "there's", "i think",
            "i feel", "i notice", "seems", "looks like", "feels like"
        };

        /// <summary>
        /// Classifies a user request into a RequestType
        /// </summary>
        public RequestType Classify(string requestText, out float confidence)
        {
            if (string.IsNullOrWhiteSpace(requestText))
            {
                confidence = 0.0f;
                return RequestType.Casual;
            }

            string lowerText = requestText.ToLower().Trim();
            
            // Calculate scores for each type
            float commandScore = CalculateCommandScore(lowerText);
            float requestScore = CalculateRequestScore(lowerText);
            float suggestionScore = CalculateSuggestionScore(lowerText);
            float casualScore = CalculateCasualScore(lowerText);

            // Find the highest score
            float maxScore = Mathf.Max(commandScore, requestScore, suggestionScore, casualScore);
            confidence = Mathf.Clamp01(maxScore);

            // Classify based on highest score
            if (maxScore == requestScore)
                return RequestType.Request;
            else if (maxScore == suggestionScore)
                return RequestType.Suggestion;
            else if (maxScore == commandScore)
                return RequestType.Command;
            else
                return RequestType.Casual;
        }

        private float CalculateCommandScore(string text)
        {
            float score = 0.0f;
            
            // Check for command indicators
            foreach (var indicator in CommandIndicators)
            {
                if (text.Contains(indicator))
                    score += 0.3f;
            }

            // Imperative sentences (often short, start with verb)
            string[] words = text.Split(' ');
            if (words.Length <= 5 && CommandIndicators.Contains(words[0]))
                score += 0.4f;

            // No question mark suggests command
            if (!text.Contains("?"))
                score += 0.1f;

            return Mathf.Clamp01(score);
        }

        private float CalculateRequestScore(string text)
        {
            float score = 0.0f;
            
            // Check for polite request indicators
            foreach (var indicator in RequestIndicators)
            {
                if (text.Contains(indicator))
                    score += 0.5f;
            }

            // Question mark suggests request
            if (text.Contains("?"))
                score += 0.2f;

            return Mathf.Clamp01(score);
        }

        private float CalculateSuggestionScore(string text)
        {
            float score = 0.0f;
            
            // Check for suggestion indicators
            foreach (var indicator in SuggestionIndicators)
            {
                if (text.Contains(indicator))
                    score += 0.4f;
            }

            // Conditional language suggests suggestion
            if (text.Contains("could") || text.Contains("might") || text.Contains("maybe"))
                score += 0.2f;

            return Mathf.Clamp01(score);
        }

        private float CalculateCasualScore(string text)
        {
            float score = 0.3f; // Base score for casual
            
            // Check for casual indicators
            foreach (var indicator in CasualIndicators)
            {
                if (text.Contains(indicator))
                    score += 0.2f;
            }

            // Longer sentences tend to be casual conversation
            if (text.Split(' ').Length > 10)
                score += 0.1f;

            return Mathf.Clamp01(score);
        }

        /// <summary>
        /// Extracts the intent or action from a request
        /// </summary>
        public string ExtractIntent(string requestText)
        {
            if (string.IsNullOrWhiteSpace(requestText))
                return string.Empty;

            // Remove polite words
            string cleaned = requestText.ToLower();
            foreach (var indicator in RequestIndicators)
            {
                cleaned = cleaned.Replace(indicator, "");
            }

            // Extract verb + object pattern
            string[] words = cleaned.Trim().Split(' ');
            if (words.Length >= 2)
            {
                // Look for command verb
                for (int i = 0; i < words.Length; i++)
                {
                    if (CommandIndicators.Contains(words[i]))
                    {
                        // Return verb + rest of sentence
                        return string.Join(" ", words.Skip(i).Take(Math.Min(5, words.Length - i)));
                    }
                }
            }

            // If no clear pattern, return first few words
            return string.Join(" ", words.Take(Math.Min(5, words.Length)));
        }
    }
}
