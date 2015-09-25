(defvar idapython-host "localhost"
  "The network address of the idapython server.")


(defvar idapython-port 8008
  "The port of our idapython server.")


;; (defvar idapython-program "/usr/bin/nc"
;;   "The network used to connect to the idapython server.")

(defvar idapython-program-arguments (list idapython-host idapython-port)
  "The arguments for the network program.")


(defvar idapython-pompt-regex "^(>>>|...) "
  "Regular expression for the python prompt.")


(defun run-idapython ()
  "Start idapython in comint mode."
  (interactive)
  (pop-to-buffer-same-window
   (make-comint-in-buffer "IDAPython" nil
                          (cons idapython-host idapython-port)))
  (idapython-mode))


(define-derived-mode idapython-interpreter-mode comint-mode "IDAPython"
  "Major mode for `run-idapython'"
  (setq comint-prompt-regexp idapython-pompt-regex)
  (setq comint-prompt-read-only t))


(defun idapython-send-region (start end)
  (interactive "r")
  (comint-send-region "*IDAPython*" start end)
  (comint-send-string "*IDAPython*" "\n"))


(defun idapython-send-buffer ()
  (interactive)
  (comint-send-string "*IDAPython*"
                      (format "execfile(\"%s\")\n" (buffer-file-name))))


(define-minor-mode idapython-mode
  "Toggle idapython minor mode."
 ;; The initial value.
 :init-value nil
 ;; The indicator for the mode line.
 :lighter " IdaPython"
 ;; The minor mode bindings.
 :keymap
 '(("\C-c\C-r" . idapython-send-region)
   ("\C-c\C-c" . idapython-send-buffer))
 :group 'idapython)


(provide 'idapython)
