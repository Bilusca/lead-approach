#!/usr/bin/env bash
# ==============================================================================
# Script de Instalação Global da Skill lead-approach
# Compatível com Google Antigravity, Anthropic Claude Code e OpenAI Codex.
# ==============================================================================

set -e

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="${SOURCE_DIR}/.agents/skills/lead-approach"

COLOR_GREEN="\033[1;32m"
COLOR_BLUE="\033[1;34m"
COLOR_YELLOW="\033[1;33m"
COLOR_RED="\033[1;31m"
COLOR_RESET="\033[0m"

echo -e "${COLOR_BLUE}======================================================${COLOR_RESET}"
echo -e "${COLOR_BLUE}    Lead Approach — Instalador Global Multi-Agente    ${COLOR_RESET}"
echo -e "${COLOR_BLUE}    (Google Antigravity · Claude Code · OpenAI Codex) ${COLOR_RESET}"
echo -e "${COLOR_BLUE}======================================================${COLOR_RESET}\n"

if [ ! -f "${SKILL_DIR}/SKILL.md" ]; then
  echo -e "${COLOR_RED}Erro: Definição da skill não encontrada em: ${SKILL_DIR}/SKILL.md${COLOR_RESET}"
  exit 1
fi

install_target() {
  local target_dir="$1"
  local name="$2"

  mkdir -p "$(dirname "${target_dir}")"
  if [ -L "${target_dir}" ] || [ -d "${target_dir}" ]; then
    rm -rf "${target_dir}"
  fi

  if [ "${COPY_MODE}" = true ]; then
    cp -r "${SKILL_DIR}" "${target_dir}"
    echo -e "  ${COLOR_GREEN}✔${COLOR_RESET} Copiado para ${COLOR_YELLOW}${name}${COLOR_RESET} -> ${target_dir}"
  else
    ln -sfn "${SKILL_DIR}" "${target_dir}"
    echo -e "  ${COLOR_GREEN}✔${COLOR_RESET} Vinculado (symlink) em ${COLOR_YELLOW}${name}${COLOR_RESET} -> ${target_dir}"
  fi
}

uninstall_target() {
  local target_dir="$1"
  local name="$2"

  if [ -L "${target_dir}" ] || [ -d "${target_dir}" ]; then
    rm -rf "${target_dir}"
    echo -e "  ${COLOR_RED}✖${COLOR_RESET} Removido de ${COLOR_YELLOW}${name}${COLOR_RESET} -> ${target_dir}"
  fi
}

install_antigravity() {
  install_target "${HOME}/.gemini/skills/lead-approach" "Antigravity (Global ~/.gemini/skills)"
  install_target "${HOME}/.gemini/antigravity-cli/skills/lead-approach" "Antigravity CLI (~/.gemini/antigravity-cli/skills)"
}

install_claude() {
  install_target "${HOME}/.claude/skills/lead-approach" "Claude Code (~/.claude/skills)"
}

install_codex() {
  install_target "${HOME}/.agents/skills/lead-approach" "OpenAI Codex (~/.agents/skills)"
  install_target "${HOME}/.codex/skills/lead-approach" "Codex CLI (~/.codex/skills)"
}

uninstall_all() {
  echo -e "${COLOR_YELLOW}Removendo links globais...${COLOR_RESET}"
  uninstall_target "${HOME}/.gemini/skills/lead-approach" "Antigravity"
  uninstall_target "${HOME}/.gemini/antigravity-cli/skills/lead-approach" "Antigravity CLI"
  uninstall_target "${HOME}/.claude/skills/lead-approach" "Claude Code"
  uninstall_target "${HOME}/.agents/skills/lead-approach" "OpenAI Codex"
  uninstall_target "${HOME}/.codex/skills/lead-approach" "Codex CLI"
  echo -e "\n${COLOR_GREEN}Desinstalação concluída com sucesso!${COLOR_RESET}"
  exit 0
}

usage() {
  echo "Uso: $0 [OPÇÕES]"
  echo ""
  echo "Opções:"
  echo "  --all             Instala a skill globalmente para Antigravity, Claude Code e Codex."
  echo "  --antigravity     Instala a skill apenas para o Google Antigravity."
  echo "  --claude          Instala a skill apenas para o Anthropic Claude Code."
  echo "  --codex           Instala a skill apenas para o OpenAI Codex."
  echo "  --copy, -c        Copia os arquivos em vez de criar links simbólicos (recomendado para npx)."
  echo "  --uninstall       Remove todos os links simbólicos instalados globalmente."
  echo "  --help, -h        Exibe esta mensagem de ajuda."
  echo ""
  echo "Exemplo:"
  echo "  ./install.sh --all"
  exit 0
}

if [ "$#" -eq 0 ]; then
  INSTALL_ALL=true
fi

while [ "$#" -gt 0 ]; do
  case "$1" in
    --all)
      INSTALL_ALL=true
      shift
      ;;
    --antigravity)
      INSTALL_AGY=true
      shift
      ;;
    --claude)
      INSTALL_CLAUDE=true
      shift
      ;;
    --codex)
      INSTALL_CODEX=true
      shift
      ;;
    --copy|-c)
      COPY_MODE=true
      shift
      ;;
    --uninstall)
      uninstall_all
      ;;
    --help|-h)
      usage
      ;;
    *)
      echo -e "${COLOR_RED}Opção inválida: $1${COLOR_RESET}"
      usage
      ;;
  esac
done

echo -e "${COLOR_YELLOW}Instalando links simbólicos para a skill...${COLOR_RESET}"

if [ "${INSTALL_ALL}" = true ]; then
  install_antigravity
  install_claude
  install_codex
else
  [ "${INSTALL_AGY}" = true ] && install_antigravity
  [ "${INSTALL_CLAUDE}" = true ] && install_claude
  [ "${INSTALL_CODEX}" = true ] && install_codex
fi

echo -e "\n${COLOR_GREEN}Pronto! A skill 'lead-approach' está configurada e disponível.${COLOR_RESET}"
echo -e "Você já pode usá-la em qualquer repositório chamando 'lead-approach' no prompt."
