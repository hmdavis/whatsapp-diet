"""Service for classifying incoming messages as questions or food entries."""

from typing import List


class MessageClassificationService:
    """Classifies messages to determine if they are questions or food entries."""
    
    QUESTION_KEYWORDS = [
        "how", "what", "why", "when", "where", "can", "could", 
        "would", "should", "do", "does", "did", "is", "are", 
        "was", "were", "will", "have", "has", "had"
    ]
    
    QUESTION_INDICATORS = [
        "recommend", "suggest", "advice", "help", "tell me"
    ]
    
    def is_question(self, message: str) -> bool:
        """
        Determine if a message is a question based on keywords and patterns.
        
        Args:
            message: The message text to classify
            
        Returns:
            True if the message appears to be a question, False otherwise
        """
        message_lower = message.lower().strip()
        
        # Check for question mark
        if "?" in message:
            return True
            
        # Check if message starts with question words
        if any(message_lower.startswith(word) for word in self.QUESTION_KEYWORDS):
            return True
            
        # Check for question indicators anywhere in the message
        if any(indicator in message_lower for indicator in self.QUESTION_INDICATORS):
            return True
            
        return False
    
    def classify_message(self, message: str) -> str:
        """
        Classify message as 'question' or 'food_entry'.
        
        Args:
            message: The message text to classify
            
        Returns:
            'question' or 'food_entry'
        """
        return "question" if self.is_question(message) else "food_entry"