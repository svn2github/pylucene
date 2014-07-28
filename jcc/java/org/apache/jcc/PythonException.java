/* ====================================================================
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 * ====================================================================
 */

package org.apache.jcc;


public class PythonException extends RuntimeException {
    public boolean withTrace = true;
    protected long py_error_state = 0L;

    public PythonException(String message)
    {
        super(message);
        saveErrorState();
    }

    public void finalize()
        throws Throwable
    {
        pythonDecRef();
    }

    public String getMessage(boolean trace)
    {
        if (py_error_state == 0L)
            return super.getMessage();

        String message = getErrorMessage();

        if (trace)
            return message + "\n" + getErrorTraceback();

        return message;
    }

    public String getMessage()
    {
        return getMessage(withTrace);
    }

    public native void pythonDecRef();

    public native String getErrorName();
    public native String getErrorMessage();
    public native String getErrorTraceback();

    protected native void saveErrorState();
}
