"""
Base Component - Open/Closed Principle
Base class for all UI components following SOLID principles
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import streamlit as st


class BaseComponent(ABC):
    """Base component class - Open/Closed Principle"""

    def __init__(self, component_id: str = None):
        self.component_id = component_id or self.__class__.__name__
        self._initialize_component()

    def _initialize_component(self) -> None:
        """Initialize component-specific state"""
        pass

    @abstractmethod
    def render(self) -> None:
        """Render component - must be implemented by subclasses"""
        pass

    def get_component_state(self, key: str, default: Any = None) -> Any:
        """Get component-specific state"""
        state_key = f"{self.component_id}_{key}"
        return st.session_state.get(state_key, default)

    def set_component_state(self, key: str, value: Any) -> None:
        """Set component-specific state"""
        state_key = f"{self.component_id}_{key}"
        st.session_state[state_key] = value

    def clear_component_state(self) -> None:
        """Clear all component-specific state"""
        keys_to_remove = [
            key
            for key in st.session_state.keys()
            if key.startswith(f"{self.component_id}_")
        ]
        for key in keys_to_remove:
            del st.session_state[key]

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "component_id": self.component_id,
            "component_type": self.__class__.__name__,
            "state_keys": [
                key
                for key in st.session_state.keys()
                if key.startswith(f"{self.component_id}_")
            ],
        }


class InteractiveComponent(BaseComponent):
    """Base class for interactive components"""

    def __init__(self, component_id: str = None, on_change: callable = None):
        super().__init__(component_id)
        self.on_change = on_change

    def handle_change(self, *args, **kwargs) -> None:
        """Handle component change events"""
        if self.on_change:
            self.on_change(*args, **kwargs)

    def render_with_callback(self, render_func: callable, *args, **kwargs) -> Any:
        """Render component with change callback"""
        result = render_func(*args, **kwargs)
        if result is not None:
            self.handle_change(result)
        return result


class ContainerComponent(BaseComponent):
    """Base class for container components"""

    def __init__(self, component_id: str = None, children: list = None):
        super().__init__(component_id)
        self.children = children or []

    def add_child(self, child: BaseComponent) -> None:
        """Add child component"""
        self.children.append(child)

    def remove_child(self, child: BaseComponent) -> None:
        """Remove child component"""
        if child in self.children:
            self.children.remove(child)

    def render_children(self) -> None:
        """Render all child components"""
        for child in self.children:
            child.render()

    def get_child_by_id(self, child_id: str) -> Optional[BaseComponent]:
        """Get child component by ID"""
        for child in self.children:
            if child.component_id == child_id:
                return child
        return None
